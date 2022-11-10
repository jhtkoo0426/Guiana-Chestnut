"""
Integrates finnhub.io methods into Guiana for stock symbol data processing, analysing and visualisation.
"""

import datetime
import time
import finnhub as fh
import requests
import csv

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
    
    def check_account_ready(self, request):
        if request.user.is_authenticated and self.check_key_valid(request.user.finnhub_api_key):
            self.initialize_client()
            return True
        return False
    
    # System function used to scrape data from finnhub
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

    def search_symbol(self, symbol: str, context: dict):
        if FinnhubSupportedStockSymbols.objects.filter(symbol_name=symbol).exists():
            financials = self.get_symbol_financials(symbol)
            candlesticks = self.get_symbol_candlesticks(symbol)
            context['financials'] = financials
            context['candlesticks'] = candlesticks
        return context

    # Auxiliary function to get a symbol's company's financial background
    def get_symbol_financials(self, symbol: str):
        return self.client.company_profile2(symbol=symbol)

    # Auxiliary function to get a symbol's quotes from 2010 onwards
    def get_symbol_candlesticks(self, symbol: str):
        RESOLUTION = 'D'
        start_date = time.mktime(
            datetime.datetime.strptime('01/01/2010', '%d/%m/%Y').timetuple()  # Timestamp of 1 Jan, 2000.
        )
        end_date = time.time()  # Current timestamp.
        
        candlesticks = self.client.stock_candles(symbol, RESOLUTION, int(start_date), int(end_date))

        # Process candlesticks for plotting with Apache ECharts
        return candlesticks
