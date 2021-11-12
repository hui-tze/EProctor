from uuid import uuid4

from django.contrib import messages
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group

from exam.models import Exam, Subject
from instructor.models import Instructor
from . import forms
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UpdateUserForm, UpdateStudentForm
from student.models import Student
from django.core.mail import EmailMessage
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2
import dlib
import threading
import os
import imutils
from imutils import face_utils
from imutils.video import VideoStream
from imutils.face_utils import FaceAligner
import cv2
import threading
from sklearn.preprocessing import LabelEncoder
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder
import numpy as np
import pickle
import os
from sklearn.svm import SVC

def studentclick_view(request):
    return render(request, 'student/studentclick.html')


def create_dataset(username):
    id = username
    if (os.path.exists('face_recognition_data/training_dataset/{}/'.format(id)) == False):
        os.makedirs('face_recognition_data/training_dataset/{}/'.format(id))
    directory = 'face_recognition_data/training_dataset/{}/'.format(id)

    # Detect face
    # Loading the HOG face detector and the shape predictpr for allignment

    print("[INFO] Loading the facial detector")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(
        'C:/Users/User/Documents/GitHub/EProctor/face_recognition_data/shape_predictor_68_face_landmarks.dat')  # Add path to the shape predictor ######CHANGE TO RELATIVE PATH LATER
    fa = FaceAligner(predictor, desiredFaceWidth=96)
    # capture images from the webcam and process and detect the face
    # Initialize the video stream
    print("[INFO] Initializing Video stream")
    vs = VideoStream(src=0).start()
    # time.sleep(2.0) ####CHECK######

    # Our identifier
    # We will put the id here and we will store the id with a face, so that later we can identify whose face it is

    # Our dataset naming counter
    sampleNum = 0
    # Capturing the faces one by one and detect the faces and showing it on the window
    while (True):
        # Capturing the image
        # vs.read each frame
        frame = vs.read()
        # Resize each image
        frame = imutils.resize(frame, width=800)
        # the returned img is a colored image but for the classifier to work we need a greyscale image
        # to convert
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # To store the faces
        # This will detect all the images in the current frame, and it will return the coordinates of the faces
        # Takes in image and some other parameter for accurate result
        faces = detector(gray_frame, 0)
        # In above 'faces' variable there can be multiple faces so we have to get each and every face and draw a rectangle around it.

        for face in faces:
            print("inside for loop")
            (x, y, w, h) = face_utils.rect_to_bb(face)

            face_aligned = fa.align(frame, gray_frame, face)
            # Whenever the program captures the face, we will write that is a folder
            # Before capturing the face, we need to tell the script whose face it is
            # For that we will need an identifier, here we call it id
            # So now we captured a face, we need to write it in a file
            sampleNum = sampleNum + 1
            # Saving the image dataset, but only the face part, cropping the rest

            if face is None:
                print("face is none")
                continue

            cv2.imwrite(directory + '/' + str(sampleNum) + '.jpg', face_aligned)
            face_aligned = imutils.resize(face_aligned, width=400)
            # cv2.imshow("Image Captured",face_aligned)
            # @params the initial point of the rectangle will be x,y and
            # @params end point will be x+width and y+height
            # @params along with color of the rectangle
            # @params thickness of the rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
            # Before continuing to the next loop, I want to give it a little pause
            # waitKey of 100 millisecond
            cv2.waitKey(50)

        # Showing the image in another window
        # Creates a window with window name "Face" and with the image img
        cv2.imshow("Don't close this window. Creating dataset...", frame)
        # Before closing it we need to give a wait command, otherwise the open cv wont work
        # @params with the millisecond of delay 1
        cv2.waitKey(1)
        # To get out of the loop
        if sampleNum > 300:
            break

    # Stoping the videostream
    vs.stop()
    # destroying all the windows
    cv2.destroyAllWindows()

def train():
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



@gzip.gzip_page
def student_signup_view(request):
    userForm = forms.StudentUserForm()
    studentForm = forms.StudentForm()
    context = {'userForm': userForm, 'studentForm': studentForm}
    if request.method == 'POST':
        userForm = forms.StudentUserForm(request.POST)
        studentForm = forms.StudentForm(request.POST, request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            create_dataset(user.username)
            student = studentForm.save()
            student.user = user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
            messages.success(request, "Sign up successfully")
            #train()
            return redirect('/student/stulogin')
        else:
            messages.error(request, "Unsuccessful sign up")

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
                messages.error(request, "Invalid sign in.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "student/stulogin.html", context)


@login_required(login_url='stulogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    context = {
        'exam': Exam.objects.all().count(),
        'subject': Subject.objects.all().count()
    }
    return render(request, 'student/student_dashboard.html',context=context)


def student_logout_request(request):
    logout(request)
    return HttpResponseRedirect('/home')


@login_required(login_url='stulogin')
def student_logout_request(request):
    logout(request)
    return HttpResponseRedirect('/home')


@login_required(login_url='stulogin')
@user_passes_test(is_student)
def view_student_profile(request, pk):
    student = Student.objects.get(user_id=pk)

    if student.studentGender == 'F':
        student.studentGender = "Female"
    else:
        student.studentGender = "Male"

    if request.method == 'POST':
        profile_form = UpdateStudentForm(request.POST,request.FILES,instance=request.user.student)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
        else:
            messages.error(request, 'Error occured')
    else:
        profile_form = UpdateStudentForm(instance=request.user.student)

    context = {
        'profile_form': profile_form,
        'student': student
    }

    return render(request, 'student/student_profile.html', context)


@login_required(login_url='stulogin')
def student_view_instructor_view(request):
    instructors = Instructor.objects.all().filter(status=True)
    return render(request, 'student/student_view_instructor.html', {'instructors': instructors})

