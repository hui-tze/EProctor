from django import forms
from django.contrib.auth.models import User
from . import models

from exam import models as QMODEL

# class StudentUserForm(forms.ModelForm):
#     class Meta:
#         model=User
#         fields=['first_name','last_name','username','password']
#         widgets = {
#         'password': forms.PasswordInput()
#         }

class DateInput(forms.DateInput):
    input_type = 'date'

GENDER_CHOICES=[
    ('M','Male'),
    ('F','Female')
]

class StudentUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model=models.Student
        fields = ['studentEmail','studentIC','studentDOB','studentContact','studentGender','studentAddress']
        widgets = {
            'studentDOB': DateInput(),
            'studentGender': forms.RadioSelect(choices=GENDER_CHOICES)
        }