from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from instructor.models import Instructor
from student.models import Student
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.db.models.query_utils import Q

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
    dict = {
        'total_teacher': Instructor.objects.all().filter(status=True).count(),
        'pending_teacher': Instructor.objects.all().filter(status=False).count()
    }
    return render(request, 'exam/admin_instructor.html', context=dict)


@login_required(login_url='adminlogin')
def admin_view_pending_instructor_view(request):
    instructors = Instructor.objects.all().filter(status=False)
    return render(request, 'exam/admin_pending_instructor.html', {'instructors': instructors})


@login_required(login_url='adminlogin')
def approve_instructor_view(request, pk):
    instructor = Instructor.objects.get(id=pk)
    instructor.status = True
    instructor.save()
    return HttpResponseRedirect('/admin-view-pending-instructor')


@login_required(login_url='adminlogin')
def reject_instructor_view(request, pk):
    instructor = Instructor.objects.get(id=pk)
    user = User.objects.get(id=instructor.user_id)
    user.delete()
    instructor.delete()
    return HttpResponseRedirect('/admin-view-pending-instructor')


def admin_logout_request(request):
    logout(request)
    return HttpResponseRedirect('/home')


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password/password_reset_email.html"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'ongs-wm18@student.tarc.edu.my', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')

    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_instructions.html",
                  context={"password_reset_form": password_reset_form})
