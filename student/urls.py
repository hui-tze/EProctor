from django.urls import path
from student import views
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('studentclick', views.studentclick_view),
    path('stusignup', views.student_signup_view,name='studentsignup'),
    path('stulogin', views.student_login_view,name='studentlogin'),
    path('studashboard', views.student_dashboard_view,name='studentdashboard'),
    path('stulogout', views.student_logout_request,name='studentlogout')
]