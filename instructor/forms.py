from django import forms
from django.contrib.auth.models import User
from . import models

class InstructorUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }

class InstructorForm(forms.ModelForm):
    class Meta:
        model=models.Instructor
        fields=['instructorEmail','instructorIC','instructorContact','instructorAddress']
        widgets = {
            'instructorEmail': forms.EmailInput()
        }

class UpdateUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['password']
        widgets = {
        'password': forms.PasswordInput()
        }

class UpdateInstructorForm(forms.ModelForm):
    class Meta:
        model=models.Instructor
        fields = ['instructorEmail','instructorContact','instructorAddress']