from django.shortcuts import render
from django.views.generic.base import View
from accounts.forms import UserAddFinnhubKeyForm
from finnhub_integration.finnhub_api import FinnhubClient
from finnhub_integration.models import FinnhubSupportedExchanges, FinnhubSupportedStockSymbols

import requests


class FinnhubMixin:
    f = FinnhubClient()
    
    
class DashboardView(FinnhubMixin, View):
    template_name = "dashboard/dashboard.html"

    def get(self, request):
        context = {}
        self.f.api_key = self.request.user.finnhub_api_key
        self.f.initialize_client()

        if self.f.check_account_ready(request):
            context = {
                'latest_news': self.f.get_latest_news()
            }
        return render(request, self.template_name, context=context)
    
    def post(self, request):
        if self.f.check_account_ready(request):
            context = {
                'latest_news': self.f.get_latest_news()
            }
        return render(request, self.template_name, context=context)


class SearchResultsView(FinnhubMixin, View):
    template_name = "dashboard/search_results.html"

    def get(self, request):
        self.f.api_key = self.request.user.finnhub_api_key
        self.f.initialize_client()

        if self.f.check_account_ready(request):
            symbol = request.GET.get('search_symbol').upper()
            context = {
                "symbol": symbol,
                "message": "Search successful!",
                "api_key": request.user.finnhub_api_key,
            }
            context = self.f.search_symbol(symbol, context)
        else:
            context = {
                "message": "Your API is invalid. Please update it or register for a new one at finnhub.io."
            }
        return render(request, self.template_name, context=context)
    
    def post(self, request):
        context = {}
        return render(request, self.template_name, context=context)

    
class UserSettingsView(View):
    template_name = "dashboard/settings.html"

    def get(self, request):
        add_key_form = UserAddFinnhubKeyForm()
        context = {
            "add_api_key_form": add_key_form,
            "message": None
        }
        return render(request, self.template_name, context=context)

    def post(self, request):
        add_key_form = UserAddFinnhubKeyForm(request.POST, instance=request.user)
        context = {}

        if add_key_form.is_valid():
            add_key_form.save()
            print(request.user.finnhub_api_key)
            context['message'] = "API key updated!"
            context['add_api_key_form'] = add_key_form
            return render(request, self.template_name, context=context)
        else:
            add_key_form = UserAddFinnhubKeyForm(instance=request.user)
            context['add_api_key_form'] = add_key_form
            return render(request, self.template_name, context=context)