from django.urls import path
from student import views
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('studentclick', views.studentclick_view),
    path('stusignup', views.student_signup_view,name='studentsignup'),
    path('stulogin', views.student_login_view,name='studentlogin'),
    path('studashboard', views.student_dashboard_view,name='studentdashboard'),
    path('stulogout', views.student_logout_request,name='studentlogout'),
    path('studentprofile/<int:pk>', views.view_student_profile,name='studentprofile'),
    path('student-view-instructor', views.student_view_instructor_view, name='student-view-instructor'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)