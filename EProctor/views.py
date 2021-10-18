from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

from instructor.models import Instructor
from student.models import Student
from django.contrib.auth.models import User

def home(request):
    return render(request, 'exam/homepage.html')

def is_instructor(user):
    return user.groups.filter(name='INSTRUCTOR').exists()

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

def adminlogin_view(request):
    form = AuthenticationForm(request, data=request.POST)
    context = {
        'form': form
    }
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            if request.user.is_superuser:
                return redirect('/admindashboard')
            else:
                messages.error(request, "Invalid sign up.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'exam/adminlogin.html', context=context)

@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict = {
        'total_student': Student.objects.all().count(),
        'total_teacher': Instructor.objects.all().filter(status=True).count()
    }
    return render(request, 'exam/admin_dashboard.html', context=dict)

@login_required(login_url='adminlogin')
def admin_instructor_view(request):
    dict={
    'total_teacher':Instructor.objects.all().filter(status=True).count(),
    'pending_teacher':Instructor.objects.all().filter(status=False).count()
    }
    return render(request,'exam/admin_instructor.html',context=dict)

@login_required(login_url='adminlogin')
def admin_view_pending_instructor_view(request):
    instructors = Instructor.objects.all().filter(status=False)
    return render(request, 'exam/admin_pending_instructor.html', {'instructors': instructors})

@login_required(login_url='adminlogin')
def approve_instructor_view(request,pk):
    instructor = Instructor.objects.get(id=pk)
    instructor.status = True
    instructor.save()
    return HttpResponseRedirect('/admin-view-pending-instructor')

@login_required(login_url='adminlogin')
def reject_instructor_view(request,pk):
    instructor=Instructor.objects.get(id=pk)
    user = User.objects.get(id=instructor.user_id)
    user.delete()
    instructor.delete()
    return HttpResponseRedirect('/admin-view-pending-instructor')

def admin_logout_request(request):
    logout(request)
    return HttpResponseRedirect('/home')


