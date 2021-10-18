from django.urls import path
from . import views

urlpatterns = [
    path('instructorclick', views.instructorclick_view),
    path('insignup', views.instructor_signup_view,name='instructorsignup'),
    path('inlogin', views.instructor_login_view,name='instructorlogin'),
    path('insdashboard', views.instructor_dashboard_view,name='instructordashboard'),
    path('inslogout', views.instructor_logout_request,name='instructorlogout')
]