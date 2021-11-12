from django import forms
from django.contrib.auth.models import User


class form(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30)


class ChangePasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password']
        widgets = {
            'password': forms.PasswordInput()
        }


class ResetPasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }
