import django_filters
from django import forms

from .models import *


class QuestionFilter(django_filters.FilterSet):
    class Meta:
        model = Question
        fields = ['subject', 'questionDesc', 'status']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['subject'].queryset = Subject.objects.all()

