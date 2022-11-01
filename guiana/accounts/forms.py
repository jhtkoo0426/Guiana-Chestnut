from django import forms
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


class UserAdminCreationForm(forms.ModelForm):
    """
    Form for creating new users.
    """

    password = forms.CharField(widget=forms.PasswordInput)
    password_2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        queryset = User.objects.filter(username=username)
        if queryset.exists():
            raise forms.ValidationError("This username has been taken. Please try a different username!")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_2")
        if password is not None and password != password_2:
            raise forms.ValidationError("Your passwords must match.")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """
    Login form for users.
    """

    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '@InspiredTrader', 'class': 'form-field'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your Password', 'class': 'form-field'})
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.active:
            raise forms.ValidationError("Invalid username or password. Please try again.")

    def login(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user


class UserRegisterForm(forms.ModelForm):
    """
    A form for creating new users.
    """

    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'placeholder': 'Pick a username', 'class': 'form-field'})
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': '8+ Characters', 'class': 'form-field'})
    )

    password_2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-type password', 'class': 'form-field'})
    )

    class Meta:
        model = User
        fields = ['username', ]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        queryset = User.objects.filter(username=username)
        if queryset.exists():
            raise forms.ValidationError("This username has been taken. Please try a different username!")
        return username
    
    def clean(self):
        password = self.cleaned_data.get('password')
        password_2 = self.cleaned_data.get('password_2')
        if password is not None and password != password_2:
            raise forms.ValidationError("Your passwords must match. Please try again!")
        return self.cleaned_data
    
    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data.get('password'))
        user.active = True
        if commit:
            user.save()
        return user