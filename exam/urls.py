from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.home, name='home'),
    path('question', views.question, name='question'),
    path('subject', views.subject, name='subject'),
    path('add_new_subject', views.add_new_subject, name='add_new_subject'),
    path('edit_subject/<str:pk>/', views.edit_subject, name='edit_subject'),
    path('delete_subject/<str:pk>/', views.delete_subject, name='delete_subject'),

    path('add_question', views.add_question, name='add_question'),
    path('edit_question/<str:pk>', views.edit_question, name='edit_question'),

    path('examination', views.examination, name='examination'),
    path('add_examination', views.add_examination, name='add_examination'),
    path('assign_student/<str:pk>/', views.assign_student, name='assign_student'),
    path('my_examination', views.my_examination, name='my_examination'),
    path('post_answer', views.post_answer, name='post_answer'),
    path('validate_code', views.validate_code, name='validate_code'),
]