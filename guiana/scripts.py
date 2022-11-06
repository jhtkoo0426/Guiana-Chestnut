import os
import finnhub as fh
from finnhub_integration.models import FinnhubSupportedExchanges, FinnhubSupportedStockSymbols

FINNHUB_KEY = os.environ.get('FINNHUB_API_KEY')

fc = fh.Client(api_key=FINNHUB_KEY)

symbols = fc.stock_symbols('US')
symbol_exchange = FinnhubSupportedExchanges.objects.get(exchange_code='US')

counter = 0
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
    counter += 1
    if counter % 10 == 0:
        print("10 symbols added!")