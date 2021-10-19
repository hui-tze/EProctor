from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.models import Group
from . import forms
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test


# Create your views here.
def studentclick_view(request):
    return render(request, 'student/studentclick.html')


def student_signup_view(request):
    userForm = forms.StudentUserForm()
    studentForm = forms.StudentForm()
    context = {'userForm': userForm, 'studentForm': studentForm}
    if request.method == 'POST':
        userForm = forms.StudentUserForm(request.POST)
        studentForm = forms.StudentForm(request.POST, request.FILES)
        if userForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            student = studentForm.save()
            student.user = user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
            messages.success(request, "Sign up successfully")
        else:
            messages.success(request, "Unsuccessful sign up")

    return render(request, 'student/stusignup.html', context=context)


def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


def student_login_view(request):
    form = AuthenticationForm(request, data=request.POST)
    context = {
        'form': form
    }
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None and user.groups.filter(name='STUDENT').exists():
                login(request, user)
                return HttpResponseRedirect('studashboard')
            else:
                messages.error(request, "Invalid sign up.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "student/stulogin.html", context)


@login_required(login_url='stulogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    return render(request, 'student/student_dashboard.html')


def student_logout_request(request):
    logout(request)
    return HttpResponseRedirect('/home')
