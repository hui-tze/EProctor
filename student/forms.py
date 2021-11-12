from django import forms
from django.contrib.auth.models import User
from . import models
import validators


class DateInput(forms.DateInput):
    input_type = 'date'


GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female')
]


class StudentUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = models.Student
        fields = ['studentEmail', 'studentIC', 'studentDOB', 'studentContact', 'studentGender', 'studentAddress',
                  'studentPic']
        widgets = {
            'studentDOB': DateInput(),
            'studentGender': forms.RadioSelect(choices=GENDER_CHOICES),
            'studentEmail': forms.EmailInput(),
        }

    def clean_contact(self):
        studentContact = self.cleaned_data.get('studentContact')
        if len(studentContact) < 10:
            raise forms.ValidationError("Contact number should contain a minimum of 10 characters")
        return studentContact

    def clean_ic(self):
        studentIC = self.cleaned_data.get('studentIC')
        if len(studentIC) < 12:
            raise forms.ValidationError("IC number should contain a minimum of 12 characters")
        return studentIC


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password']
        widgets = {
            'password': forms.PasswordInput()
        }


class UpdateStudentForm(forms.ModelForm):
    class Meta:
        model = models.Student
        fields = ['studentEmail', 'studentContact', 'studentAddress', 'studentPic']


class StudentVerificationForm(forms.ModelForm):
    class Meta:
        model = models.Student
        fields = ['studentIC']
