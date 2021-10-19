"""EProctor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from EProctor import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('exam/', include('exam.urls')),
    path('student/', include('student.urls')),
    path('instructor/', include('instructor.urls')),
    path('home', views.home, name='home'),
    path('adminlogin/', views.adminlogin_view),
    path('admindashboard', views.admin_dashboard_view,name='exam-dashboard'),
    path('admininstructor', views.admin_instructor_view,name='admin-instructor'),
    path('admin-view-pending-instructor', views.admin_view_pending_instructor_view,name='admin-view-pending-instructor'),
    path('approve-instructor/<int:pk>', views.approve_instructor_view,name='approve-instructor'),
    path('reject-teacher/<int:pk>', views.reject_instructor_view,name='reject-teacher'),
    path('adminlogout', views.admin_logout_request,name='adminlogout')
]
