from django import forms
from django.contrib.auth.models import User

class form(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30)