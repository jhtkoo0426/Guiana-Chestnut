from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.generic import View

from .forms import UserLoginForm, UserRegisterForm


class LoginPageView(View):
    template_name = "authentication/login.html"
    
    def get(self, request):
        login_form = UserLoginForm()
        message = ""

        context = {
            "login_form": login_form,
            "message": message
        }
        return render(request, self.template_name, context=context)
    
    def post(self, request):
        login_form = UserLoginForm(request.POST)

        if login_form.is_valid():
            user = authenticate(
                username=login_form.cleaned_data["username"],
                password=login_form.cleaned_data["password"],
            )

            if user is not None:
                login(request, user)
                return redirect('dashboard')
        
        message = "Login failed. Please enter the correct username or password."
        
        context = {
            "login_form": login_form,
            "message": message
        }
        return render(request, self.template_name, context=context)


class RegisterPageView(View):
    template_name = "authentication/register.html"

    def get(self, request):
        register_form = UserRegisterForm()
        message = ""

        context = {
            "register_form": register_form,
            "message": message
        }
        return render(request, self.template_name, context=context)

    def post(self, request):
        register_form = UserRegisterForm(request.POST)

        if register_form.is_valid():
            register_form.save()
            return redirect('login')
        else:
            context = {
                "register_form": register_form
            }
            return render(request, self.template_name, context=context)
        

class LogoutPageView(View):
    def get(self, request):
        logout(request)
        return redirect('login')