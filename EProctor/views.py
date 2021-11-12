from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from traits.trait_types import self

from EProctor import forms
from EProctor.forms import ChangePasswordForm, ResetPasswordForm
from exam.models import Subject
from instructor.models import Instructor
from student.models import Student
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.db.models.query_utils import Q
from django.core.mail import EmailMessage
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2
import threading
from sklearn.preprocessing import LabelEncoder
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder
import numpy as np
import pickle
import os
from sklearn.svm import SVC


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
        'total_teacher': Instructor.objects.all().filter(status=True).count(),
        'pending_teacher': Instructor.objects.all().filter(status=False).count(),
        'total_courses': Subject.objects.all().count()
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


@login_required(login_url='adminlogin')
def admin_view_instructor_view(request):
    instructors = Instructor.objects.all().filter(status=True)
    return render(request, 'exam/admin_view_instructor.html', {'instructors': instructors})


@login_required(login_url='adminlogin')
def admin_view_student_view(request):
    students = Student.objects.all()
    # students = User.objects.all()
    # user.groups.filter(name='STUDENT').exists()

    if request.GET.get('sname'):
        studentName = request.GET.get('sname')
        students = students.filter(studentEmail__icontains=studentName)
    return render(request,'exam/admin_view_student.html',{'students':students})


def admin_logout_request(request):
    logout(request)
    return HttpResponseRedirect('/home')


def change_password_request(request, pk):
    person = User.objects.get(id=pk)
    if request.method == "POST":
        password_change_form = ChangePasswordForm(request.POST,request.FILES,instance=request.user)
        if password_change_form.is_valid():
            user = password_change_form.save()
            user.set_password(user.password)
            user.save()
            messages.success(request, "Password updated successfully")
        else:
            messages.error(request, "Unsuccessful password update")

    else:
        password_change_form = ChangePasswordForm()

    return render(request=request, template_name="password/change_password.html",
                  context={"password_change_form": password_change_form})


def user_acc_verification(request):
    if request.method == "POST":
        user_name = request.POST["username"]

        if User.objects.filter(username=user_name).exists():
            uid = User.objects.get(username=user_name).id
            return redirect('reset_password', pk=uid)
        else:
            messages.error(request, "Username does not exist")

    return render(request, template_name="password/user_acc_verification.html")

def reset_password_request(request, pk):
    username = User.objects.get(id=pk)
    if request.method == "POST":
        user = User.objects.get(id=pk)
        password_change_form = ChangePasswordForm(request.POST, request.FILES, instance=user)
        if password_change_form.is_valid():
            user = password_change_form.save()
            user.set_password(user.password)
            user.save()
            messages.success(request, "Password updated successfully")
        else:
            messages.error(request, "Unsuccessful password update")

    else:
        password_change_form = ChangePasswordForm()

    return render(request, template_name="password/reset_password.html",
                  context={"password_change_form": password_change_form, 'username': username})

@gzip.gzip_page
def Home(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
    return render(request, 'app1.html')

#to capture video class
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def train(request):
    training_dir = 'C:/Users/User/Documents/GitHub/EProctor/exam/face_recognition_data/training_dataset'

    count = 0
    for person_name in os.listdir(training_dir):
        curr_directory = os.path.join(training_dir, person_name)
        if not os.path.isdir(curr_directory):
            continue
        for imagefile in image_files_in_folder(curr_directory):
            count += 1

    X = []
    y = []
    i = 0

    for person_name in os.listdir(training_dir):
        print(str(person_name))
        curr_directory = os.path.join(training_dir, person_name)
        if not os.path.isdir(curr_directory):
            continue
        for imagefile in image_files_in_folder(curr_directory):
            print(str(imagefile))
            image = cv2.imread(imagefile)
            try:
                X.append((face_recognition.face_encodings(image)[0]).tolist())

                y.append(person_name)
                i += 1
            except:
                print("removed")
                os.remove(imagefile)

    targets = np.array(y)
    encoder = LabelEncoder()
    encoder.fit(y)
    y = encoder.transform(y)
    X1 = np.array(X)
    print("shape: " + str(X1.shape))
    np.save('C:/Users/User/Documents/GitHub/EProctor/face_recognition_data/classes.npy', encoder.classes_)
    svc = SVC(kernel='linear', probability=True)
    svc.fit(X1, y)
    svc_save_path = "C:/Users/User/Documents/GitHub/EProctor/face_recognition_data/svc.sav"
    with open(svc_save_path, 'wb') as f:
        pickle.dump(svc, f)

    print('Dataset training completed')
    return redirect('/admindashboard')

def handle_not_found(request, exception):
    return render(request,'404error.html')