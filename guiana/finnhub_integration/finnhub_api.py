"""
Integrates finnhub.io methods into Guiana for stock symbol data processing, analysing and visualisation.
"""

import datetime
import pytz
import time
import finnhub as fh
import requests
import csv
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

from finnhub_integration.models import FinnhubSupportedExchanges, FinnhubSupportedStockSymbols


class FinnhubClient:
    def __init__(self):
        """
        Construct a new finnhub.io Client instance.

        @return: returns nothing
        """

        self.api_key = None
        self.client = None
        self.API_URL = "https://finnhub.io/api/v1/?token="

        self.nlp = spacy.load('en_core_web_lg')
        self.nlp.add_pipe('spacytextblob')
    
        
    def update_key(self, key: str):
        """
        Updates the current api_key with a new key; If no key was previously set, 
        use the key as the current key.

        @param key: a registered API key from finnhub.io
        @return: returns nothing
        """

        if self.check_key_valid(key):
            self.api_key = key
        else:
            raise ValueError("The API key you entered is invalid or has expired. Pleas try again.")
    
        
    def check_key_valid(self, key):
        """
        Sends a request to finnhub.io to validate the provided key.
        @return: Returns True if the key is valid, False otherwise.
        """
        
        url = self.API_URL + key
        
        # Check if exception is raised for any endpoint
        r = requests.get(url)
        return r.status_code != 401

    
    def initialize_client(self):
        """
        Establish a connection to the Finnhub API using the current api key.

        @return: returns nothing
        """

        self.client = fh.Client(api_key=self.api_key)

        
    def check_account_ready(self, request):
        if request.user.is_authenticated and self.check_key_valid(request.user.finnhub_api_key):
            self.initialize_client()
            return True
        return False
    
    
    # Helper functions
    def calc_now_timestamp(self):
        """
        Calculate the current timestamp.
        """
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp()
        return now
    
    def calc_date_from_timestamp(self, timestamp, format):
        """
        Calculate the date from the provided timestamp with a specific format.

        @param timestamp: Python datetime utx timestamp instance.
        @param format: String format for the calculated timestamp.
        """
        return datetime.datetime.fromtimestamp(timestamp).strftime(format)

    def calc_date_delta_from_timestamp(self, timestamp, days_ago, format):
        """
        Calculate the date n days ago from the provided timestamp with a specific format.

        @param timestamp: Python datetime utx timestamp instance.
        @param delta: Days delta.
        @param format: String format for the calculated timestamp.
        """
        date_delta = timestamp - days_ago * 24 * 60 * 60
        return datetime.datetime.fromtimestamp(date_delta).strftime(format)

    def calc_time_delta_from_now(self, timestamp):
        """
        Calculate the time difference between now and a given timestamp, in days and hours.

        @param timestamp: Python datetime utx timestamp instance.
        """
        now = self.calc_now_timestamp()
        delta = int(now) - int(timestamp)
        days = delta // 86400
        hours = (delta - days * 86400) // 3600
        return str(days) + " days, " + str(hours) + " hours ago"


    # System functions used to scrape data from finnhub
    # These functions should be moved to a task scheduler in the future
    def download_symbols(self):
        symbols = self.client.stock_symbols('US')
        symbol_exchange = FinnhubSupportedExchanges.objects.get(exchange_code='US')

        for symbol in symbols:
            symbol_obj = FinnhubSupportedStockSymbols.objects.create(
                symbol_exchange_code = symbol_exchange,
                symbol_currency = symbol['currency'],
                symbol_description = symbol['description'],
                symbol_type = symbol['type'],
                symbol_display_sym = symbol['displaySymbol'],
                symbol_name = symbol['symbol']
            )
            symbol_obj.save()

            
    # TODO: Convert this function to scheduled function (via celery)
    def import_supported_exchanges(self):
        """
        Import a list of supported exchanges from finnhub.io.

        @return: returns nothing
        """

        with open('../Finnhub Exchanges.csv', newline='') as f:
            reader = csv.reader(f)
            next(reader)    # To skip the labels row
            
            for row in reader:
                # ['code', 'name', 'mic', 'timezone', 'hour', 'close_date', 'country', 'source', '']
                new_exchange = FinnhubSupportedExchanges.objects.create(
                    exchange_code = row[0],
                    exchange_name = row[1],
                    exchange_timezone = row[3],
                    exchange_country = row[6]
                )
                new_exchange.save()
                print('New exchange data saved to db')


    # General functions
    def get_latest_news(self):
        # https://finnhub.io/docs/api/market-news
        return self.client.general_news('general', min_id=0)[:10]
    

    # Symbol-specific functions
    def search_symbol(self, symbol: str, context: dict):
        if FinnhubSupportedStockSymbols.objects.filter(symbol_name=symbol).exists():
            found_symbol_obj = FinnhubSupportedStockSymbols.objects.get(symbol_name=symbol)
            general_info = self.get_symbol_info(symbol)
            last_quote = self.get_symbol_last_quote(symbol)
            all_news, polarity_av, subjectivity_av = self.get_symbol_news(symbol)

            context['sym_obj'] = found_symbol_obj
            context['sym'] = symbol
            context['sym_country'] = general_info['country']
            context['sym_currency'] = general_info['currency']
            context['sym_exchange'] = general_info['exchange']
            context['sym_name'] = general_info['name']
            context['sym_url'] = general_info['weburl']
            context['sym_industry'] = general_info['finnhubIndustry']
            context['sym_marketCap'] = general_info['marketCapitalization']
            context['sym_logo'] = general_info['logo']
            context['sym_last_close'] = last_quote['c']
            context['sym_ytd_close'] = self.get_ytd_close(symbol)
            context['candlesticks'] = self.get_symbol_candlesticks(symbol)
            context['financials'] = self.get_symbol_financials(symbol)
            context['news'] = all_news
            context['news_polarity'] = polarity_av
            context['news_subjectivity'] = subjectivity_av
        return context

    
    # Auxiliary function to get a symbol's company's general information
    def get_symbol_info(self, symbol: str):
        return self.client.company_profile2(symbol=symbol)

    
    # Auxiliary function to get a symbol's quotes from 2010 onwards
    def get_symbol_candlesticks(self, symbol: str):
        RESOLUTION = 'D'
        start_date = time.mktime(
            datetime.datetime.strptime('01/01/2010', '%d/%m/%Y').timetuple()  # Timestamp of 1 Jan, 2000.
        )
        end_date = time.time()  # Current timestamp.
        
        candlesticks_json = self.client.stock_candles(symbol, RESOLUTION, int(start_date), int(end_date))
        candlesticks_json['t'] = [datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d') for x in candlesticks_json['t']]
        
        # Process candlesticks for plotting with Apache ECharts
        processed = {
            't': candlesticks_json['t'],
            'data': [list(i) for i in zip(candlesticks_json['o'], candlesticks_json['c'], candlesticks_json['l'], candlesticks_json['h'])]
        }
        return processed

    
    def get_symbol_last_quote(self, symbol: str):
        return self.client.quote(symbol)

        
    def get_ytd_close(self, symbol: str):
        weekday_int = datetime.datetime.today().weekday()
        today = int(datetime.datetime.now(pytz.timezone('US/Central')).timestamp())

        # Check if today is Monday (weekday=0) or Sunday (weekday=6)
        if weekday_int == 6:
            yesterday = today - 2 * 24 * 60 * 60
        elif weekday_int == 0:
            yesterday = today - 3 * 24 * 60 * 60
        else:
            yesterday = today - 24 * 60 * 60
        ytd_quote = self.client.stock_candles(symbol=symbol, resolution='D', _from=yesterday, to=today)
        return ytd_quote['c'][0]
    

    def get_symbol_financials(self, symbol: str):
        # https://finnhub.io/docs/api/company-basic-financials
        financials = self.client.company_basic_financials(symbol, 'all')['metric']
        metrics = {
            "52-week range": str(financials["52WeekLow"]) + " - " + str(financials["52WeekHigh"]),
            "Beta (5Y, monthly)": financials["beta"],
            "EPS (TTM)": financials["epsExclExtraItemsTTM"],
            "Payout Ratio (Annual)": financials["payoutRatioAnnual"],
            "Payout Ratio (TTM)": financials["payoutRatioTTM"],
        }
        return metrics
    

    def get_symbol_news(self, symbol: str):
        """
        Fetch one week worth of related news of a symbol.
        Resource: https://finnhub.io/docs/api/company-news

        @returns: List of related news
        """

        now = self.calc_now_timestamp()
        now_date = self.calc_date_from_timestamp(now, "%Y-%m-%d")
        week_ago = self.calc_date_delta_from_timestamp(now, 7, "%Y-%m-%d")
        all_news = self.client.company_news(symbol, _from=week_ago, to=now_date)
        polarities, subjectivities = 0, 0
        
        for news in all_news:
            news['upload_timedelta'] = self.calc_time_delta_from_now(news['datetime'])
            news_polarity, news_subjectivity = self.news_sentiment_analysis(news['summary'])
            news['polarity'] = round(news_polarity, 2)
            news['subjectivity'] = round(news_subjectivity, 2)
            polarities += news_polarity
            subjectivities += news_subjectivity
        polarities_avg = round(polarities / len(all_news), 4)
        subjectivities_avg = round(subjectivities / len(all_news), 4)
        return all_news, polarities_avg, subjectivities_avg
    
    def news_sentiment_analysis(self, summary: str):
        analysis = self.nlp(summary)
        news_sentiment = analysis._.blob.sentiment
        polarity, subjectivity = news_sentiment.polarity, news_sentiment.subjectivity
        return polarity, subjectivity