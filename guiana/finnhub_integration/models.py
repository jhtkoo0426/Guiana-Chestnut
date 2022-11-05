from django.db import models


class FinnhubSupportedExchanges(models.Model):
    exchange_code = models.CharField(max_length=4, blank=False, null=True, unique=True)
    exchange_name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    exchange_timezone = models.CharField(max_length=100, blank=True, null=True, unique=False)
    exchange_country = models.CharField(max_length=100, blank=False, null=True, unique=False)


class FinnhubSupportedStockSymbols(models.Model):
    symbol_exchange_code = models.ForeignKey(FinnhubSupportedExchanges, on_delete=models.CASCADE)
    symbol_currency = models.CharField(max_length=100, blank=False, null=True, unique=False)
    symbol_description = models.CharField(max_length=200, blank=True, null=True, unique=False)
    symbol_type = models.CharField(max_length=100, blank=False, null=True, unique=False)

    # Normally symbol_display_sym should be the same as symbol_name
    symbol_display_sym = models.CharField(max_length=100, blank=True, null=True, unique=True)
    symbol_name = models.CharField(max_length=100, blank=True, null=True, unique=True)