from django.shortcuts import render
from django.views.generic.base import View
from accounts.forms import UserAddFinnhubKeyForm


class DashboardView(View):
    template_name = "dashboard/dashboard.html"

    def get(self, request):
        context = {}
        return render(request, self.template_name, context=context)
    
    def post(self, request):
        context = {}
        return render(request, self.template_name, context=context)


class SearchResultsView(View):
    template_name = "dashboard/search_results.html"

    def get(self, request):
        symbol = request.GET.get('search_symbol')
        context = {
            "results": symbol
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