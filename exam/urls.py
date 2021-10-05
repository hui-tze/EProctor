from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('question', views.question, name='question'),
    path('subject', views.subject, name='subject'),
    path('add_new_subject', views.add_new_subject, name='add_new_subject'),
    path('validate_code', views.validate_code, name='validate_code'),
]