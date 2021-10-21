from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import ModelForm, widgets, DateInput
from .models import *
from django import forms


class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
            }
        }


class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['subject', 'questionDesc']


class ExamForm(ModelForm):
    class Meta:
        model = Exam
        fields = ['examDate']

    widgets = {
        'examDate': forms.DateField(widget=forms.SelectDateWidget())
    }

