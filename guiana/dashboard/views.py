from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View


class SearchTickerMixin:
    def get_ticker(self, request):
        return request.POST.get('search_symbol')    # Form field name responsible for fetching user input of target symbol
    
    def redirect_symbol_as_kwargs(self, request):
        return redirect(reverse('search_results', kwargs={'symbol': self.get_ticker(request)}))
    
    def search_ticker(self, symbol):
        return symbol.upper()


class DashboardView(SearchTickerMixin, View):
    template_name = "dashboard/dashboard.html"

    def get(self, request):
        context = {}
        return render(request, self.template_name, context=context)
    
    def post(self, request):
        return self.redirect_symbol_as_kwargs(request)


class SearchResultsView(SearchTickerMixin, View):
    template_name = "dashboard/search_results.html"

    def get(self, request, symbol):
        results = self.search_ticker(symbol)
        context = {
            "results": results
        }
        return render(request, self.template_name, context=context)
    
    def post(self, request, symbol):
        return self.redirect_symbol_as_kwargs(request)