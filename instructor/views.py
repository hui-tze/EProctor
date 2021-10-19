from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect

from student.models import Student
from . import forms
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.
from .models import Instructor


def instructorclick_view(request):
    return render(request, 'instructor/instructorclick.html')


def instructor_signup_view(request):
    userForm = forms.InstructorUserForm()
    insForm = forms.InstructorForm()
    mydict = {'userForm': userForm, 'insForm': insForm}
    if request.method == 'POST':
        userForm = forms.InstructorUserForm(request.POST)
        insForm = forms.InstructorForm(request.POST, request.FILES)
        if userForm.is_valid() and insForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            ins = insForm.save(commit=False)
            ins.user = user
            ins.save()
            my_instructor_group = Group.objects.get_or_create(name='INSTRUCTOR')
            my_instructor_group[0].user_set.add(user)
        else:
            messages.success(request, "Unsuccessful sign up")
    return render(request, 'instructor/insignup.html', context=mydict)


def is_instructor(user):
    return user.groups.filter(name='INSTRUCTOR').exists()


def instructor_login_view(request):
    form = AuthenticationForm(request, data=request.POST)
    context = {
        'form': form
    }
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None and user.groups.filter(name='INSTRUCTOR').exists():
                login(request, user)
                accountapproval = Instructor.objects.all().filter(user_id=request.user.id, status=True)
                if accountapproval:
                    return HttpResponseRedirect('insdashboard')
                else:
                    return render(request, 'instructor/ins_waiting_approval.html')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid sign up.")

    return render(request, "instructor/inlogin.html", context)


@login_required(login_url='inslogin')
@user_passes_test(is_instructor)
def instructor_dashboard_view(request):
    context = {

        'total_student': Student.objects.all().count()
    }
    return render(request, 'instructor/instructor_dashboard.html', context=context)


def instructor_logout_request(request):
    logout(request)
    return HttpResponseRedirect('/home')
