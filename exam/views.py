import cv2
from datetime import date, datetime
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from requests import Response
from student.forms import StudentVerificationForm
from student.models import Student
from .filters import QuestionFilter
from .models import *
from student.models import Student
from .forms import *
from exam.camera import VideoCamera, IPWebCam, MaskDetect, LiveWebCam
from django.shortcuts import render
from django.http.response import StreamingHttpResponse
import pickle
import dlib
import imutils
from imutils import face_utils
import numpy as np
from sklearn.preprocessing import LabelEncoder
import face_recognition
from imutils.face_utils import FaceAligner
from imutils.video import VideoStream
import random
from liveness_verification import f_liveness_detection
from liveness_verification import liveness_questions as questions


# Create your views here.
def home(request):
    return render(request, 'index.html')


def question(request):
    all_questions = Question.objects.all()

    if request.GET.get('subject'):
        sub = request.GET.get('subject')
        all_questions = all_questions.filter(subject=sub)
    if request.GET.get('ques'):
        ques = request.GET.get('ques')
        all_questions = all_questions.filter(questionDesc__icontains=ques)
    if request.GET.get('status'):
        status = request.GET.get('status')
        all_questions = all_questions.filter(status=status)

    page = request.GET.get('page', 1)
    paginator = Paginator(all_questions, 5)
    try:
        all_question = paginator.page(page)
    except PageNotAnInteger:
        all_question = paginator.page(1)
    except EmptyPage:
        all_question = paginator.page(paginator.num_pages)

    all_subject = Subject.objects.all()
    all_answer = Answer.objects.all()
    context = {
        'all_question': all_question,
        'all_subject': all_subject,
        'all_answer': all_answer,
    }
    return render(request, 'questions/questionbank.html', context)


def subject(request):
    all_subject = Subject.objects.all()
    context = {
        'all_subject': all_subject
    }
    return render(request, 'subjects/subject.html', context)


def add_new_subject(request):
    form = SubjectForm(request.POST)

    if request.method == 'POST':
        subject_code = request.POST["subjectCode"]
        if Subject.objects.filter(subjectCode=subject_code).exists():
            messages.warning(request, "Subject Code already Exists")
            return render(request, 'subjects/subjectForm.html', {'form': form})
        else:
            if form.is_valid():
                form.save()
                messages.success(request, "Add Subject Successfully")
                return redirect('/exam/subject')
    else:
        form = SubjectForm()
    return render(request, 'subjects/subjectForm.html', {'form': form})


def edit_subject(request, pk):
    sub = Subject.objects.get(subjectID=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=sub)
        subject_code = request.POST["subjectCode"]

        if form.is_valid():
            form.save()
            messages.success(request, "Subject Updated Successfully!")
            return redirect('/exam/subject')
    else:
        form = SubjectForm(instance=sub)
    return render(request, 'subjects/subjectForm.html', {'form': form})


def delete_subject(request, pk):
    sub = Subject.objects.get(subjectID=pk)
    sub.delete()
    return redirect('/exam/subject')


def add_question(request):
    all_subject = Subject.objects.all()
    all_answer = Answer.objects.all()
    context = {
        'all_subject': all_subject,
        'all_answer': all_answer
    }

    if request.method == 'POST':
        today = date.today()
        d1 = today.strftime("%Y%m%d")
        sub = request.POST["subject"]
        question = request.POST["question"]
        correct = request.POST["correct"]
        count = Question.objects.filter(questionID__contains=d1).count()
        count = count + 1
        print(count)
        questionID = str(d1) + str(count)
        question_info = Question(questionID=questionID, questionDesc=question, subject=sub, status='A')
        question_info.save()
        for x in range(4):
            option = request.POST["option" + str(x + 1)]
            if str(correct) == str(x + 1):
                answer_info = Answer(answerDesc=option, question=questionID, rightAns='T')
            else:
                answer_info = Answer(answerDesc=option, question=questionID, rightAns='F')
            answer_info.save()
        messages.success(request, "Add Question Successfully")
        return redirect('/exam/question')
    return render(request, 'questions/addQuestion.html', context)


def edit_question(request, pk):
    editQues = Question.objects.get(questionID=pk)
    editAns = Answer.objects.filter(question=editQues.questionID)

    all_subject = Subject.objects.all()
    all_answer = Answer.objects.all()
    context = {
        'all_subject': all_subject,
        'all_answer': all_answer,
        'editQues': editQues,
        'editAns': editAns,
        'True': 'T',
        'Active': 'A'
    }

    if request.method == 'POST':
        sub = request.POST["subject"]
        question = request.POST["question"]
        correct = request.POST["correct"]
        status = request.POST["status"]
        Question.objects.filter(questionID=pk).update(questionDesc=question, subject=sub, status=status)
        i = 0
        for x in editAns:
            option = request.POST["option" + str(i + 1)]
            if str(correct) == str(i + 1):
                Answer.objects.filter(answerID=x.answerID).update(answerDesc=option, rightAns='T')
            else:
                Answer.objects.filter(answerID=x.answerID).update(answerDesc=option, rightAns='F')
            i += 1
        messages.success(request, "Add Question Successfully")
        return redirect('/exam/question')
    else:
        return render(request, 'questions/addQuestion.html', context)
    return render(request, 'questions/addQuestion.html', context)


def validate_code(request):
    subject_code = request.GET.get('subject_code', None)
    data = {
        'is_taken': Subject.objects.filter(subjectID=subject_code).exists()
    }
    if data['is_taken']:
        data['error_message'] = "Subject Code already exists."
    return JsonResponse(data)


def examination(request):
    all_exam = Exam.objects.all()
    all_subject = Subject.objects.all()
    context = {
        'all_exam': all_exam,
        'all_subject': all_subject
    }
    return render(request, 'examination/examination.html', context)


def add_examination(request):
    all_subject = Subject.objects.all()
    context = {
        'all_subject': all_subject
    }
    if request.method == 'POST':
        today = date.today()
        d1 = today.strftime("%Y%m%d")
        sub = request.POST["subject"]
        examDate = request.POST["date"]
        startTime = request.POST["stime"]
        endTime = request.POST["etime"]
        quesNum = request.POST["num"]

        exam_info = Exam(subject=sub, examDate=examDate, startTime=startTime, duration=3,
                         endTime=endTime, quesNum=quesNum, status='A')
        exam_info.save()
        messages.success(request, "Add Examination Successfully")
        return redirect('/exam/examination')
    return render(request, 'examination/examinationForm.html', context)


def my_examination(request, id):
    schedule_exam = StudentExam.objects.filter(studentID=id).count()
    context = {
        'total_exam': schedule_exam,
        'id': id
    }
    return render(request, 'examination/studentExam.html', context)


def my_exam_list(request, id):
    schedule_exam = StudentExam.objects.filter(studentID=id)
    all_exams = Exam.objects.all()
    all_subjects = Subject.objects.all()
    context = {
        'my_exam': schedule_exam,
        'all_exams': all_exams,
        'all_subjects': all_subjects
    }
    return render(request, 'examination/student_examlist.html', context)


def exam_rules(request, id):
    exam = StudentExam.objects.filter(sdID=id)
    for e in exam:
        exam_info = Exam.objects.filter(examID=e.examID)
    all_subjects = Subject.objects.all()
    if not StudentAnswer.objects.filter(sdID=id).exists():
        for e in exam_info:
            all_questions = Question.objects.filter(subject=e.subject, status='A').order_by('?')[:e.quesNum]
        for ques in all_questions:
            ques_ans = StudentAnswer(questionID=ques.questionID, sdID=id)
            ques_ans.save()

    context = {
        'exam_info': exam_info,
        'all_subjects': all_subjects,
        'id': id
    }
    return render(request, 'examination/examinationRules.html', context)


def start_exam(request, id):
    exam = StudentExam.objects.filter(sdID=id)
    for e in exam:
        exam_info = Exam.objects.filter(examID=e.examID)
    all_questions = Question.objects.all()
    student_question = StudentAnswer.objects.filter(sdID=id)
    all_answer = Answer.objects.all()
    count = StudentAnswer.objects.filter(sdID=id).count()
    for t in exam_info:
        dt = datetime.combine(t.examDate, t.endTime)
        timestamp = datetime.timestamp(dt) * 1000
        print(timestamp)

    context = {
        'student_question': student_question,
        'all_questions': all_questions,
        'all_answer': all_answer,
        'count': count,
        'id': id,
        'exam_info': exam_info,
        'timestamp': timestamp
    }

    return render(request, 'examination/startExam.html', context)


def post_answer(request):
    if request.is_ajax():
        choice = request.POST.get('value', None)
        ques = request.POST.get('qid', None)
        sdID = request.POST.get('sdID', None)
        print(choice)
        StudentAnswer.objects.filter(questionID=ques, sdID=sdID).update(studAns=choice)
        response = {
            'msg': 'Your form has been submitted successfully'  # response message
        }
        return JsonResponse(response)  # return response as JSON


def assign_student(request, pk):
    all_students = Student.objects.all()
    exam = Exam.objects.filter(examID=pk)
    studentExam = StudentExam.objects.filter(examID=pk)
    if StudentExam.objects.filter(examID=pk).exists():
        edit = "T"
    else:
        edit = 'F'
    count = Student.objects.all().count()
    context = {
        'all_students': all_students,
        'exam': exam,
        'count': count,
        'student_exam': studentExam,
        'edit': edit
    }

    if request.method == 'POST':
        if edit == 'F':
            for x in range(count):
                checkbox = "checkbox" + str(x + 1)
                if checkbox in request.POST:
                    stud = request.POST[checkbox]
                    print(request.POST[checkbox])
                    exam_student_info = StudentExam(examID=pk, studentID=stud, status='P')
                    exam_student_info.save()
        else:
            x = 0
            for student in all_students:
                checkbox = "checkbox" + str(x + 1)
                if checkbox in request.POST:
                    stud = request.POST[checkbox]
                    if not StudentExam.objects.filter(studentID=stud).exists():
                        print(request.POST[checkbox])
                        exam_student_info = StudentExam(examID=pk, studentID=stud, status='P')
                        exam_student_info.save()
                else:
                    if StudentExam.objects.filter(studentID=student.user.id).exists():
                        studExam = StudentExam.objects.get(studentID=student.user.id)
                        studExam.delete()
                x += 1
        messages.success(request, "Assign Student Successfully")
        return redirect('/exam/examination')
    return render(request, 'examination/assignStudent.html', context)

    return render(request, 'examination/startExam.html', context)


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
    return StreamingHttpResponse(gen(VideoCamera()), content_type='multipart/x-mixed-replace; boundary=frame')


def webcam_feed(request):
    return StreamingHttpResponse(gen(IPWebCam()), content_type='multipart/x-mixed-replace; boundary=frame')


def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


@user_passes_test(is_student)
def verification_before_exam(request, id):
    exam = StudentExam.objects.filter(sdID=id)

    verification_form = StudentVerificationForm(instance=request.user.student)
    context = {'verification_form': verification_form, 'id': id}

    return render(request, 'examination/verification_before_exam.html', context)


def successful_verification(request, id):
    exam = StudentExam.objects.filter(sdID=id)
    verification_form = StudentVerificationForm(instance=request.user.student)

    context = {
        'verification_form': verification_form,
        'exam': exam,
        'id': id
    }
    messages.success(request, "Student identity verified successfully")
    return render(request, 'examination/successful_verification.html', context)

def predict(face_aligned, svc, threshold=0.7):
    face_encodings = np.zeros((1, 128))
    try:
        x_face_locations = face_recognition.face_locations(face_aligned)
        faces_encodings = face_recognition.face_encodings(face_aligned, known_face_locations=x_face_locations)
        if (len(faces_encodings) == 0):
            return ([-1], [0])

    except:

        return ([-1], [0])

    prob = svc.predict_proba(faces_encodings)
    result = np.where(prob[0] == np.amax(prob[0]))
    if (prob[0][result[0]] <= threshold):
        return ([-1], prob[0][result[0]])

    return (result[0], prob[0][result[0]])


# instantiate camera
#cv2.namedWindow('Liveness Detection')
cam = cv2.VideoCapture(0)

# parameters
COUNTER, TOTAL = 0, 0
counter_ok_questions = 0
counter_ok_consecutives = 0
limit_consecutives = 2
limit_questions = 6
counter_try = 0
limit_try = 50


def show_image(cam, text, color=(0, 0, 255)):
    ret, im = cam.read()
    im = imutils.resize(im, width=720)
    im = cv2.flip(im, 1)
    cv2.putText(im, text, (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)
    return im


def verification_exam(request, id):
    COUNTER, TOTAL = 0, 0
    counter_ok_questions = 0
    counter_ok_consecutives = 0
    limit_consecutives = 2
    limit_questions = 6
    counter_try = 0
    limit_try = 50
    global user_name
    global liveTest
    cam = cv2.VideoCapture(0)

    for i_questions in range(0, limit_questions):
        # random questions generator
        index_question = random.randint(0, 2)
        question = questions.question_bank(index_question)

        # ---------------------------------------------------------
        detector = dlib.get_frontal_face_detector()

        predictor = dlib.shape_predictor(
            'C:/Users/User/Documents/GitHub/EProctor/face_recognition_data/shape_predictor_68_face_landmarks.dat')  # Add path to the shape predictor ######CHANGE TO RELATIVE PATH LATER
        svc_save_path = "C:/Users/User/Documents/GitHub/EProctor/face_recognition_data/svc.sav"

        with open(svc_save_path, 'rb') as f:
            svc = pickle.load(f)
        fa = FaceAligner(predictor, desiredFaceWidth=96)
        encoder = LabelEncoder()
        encoder.classes_ = np.load('C:/Users/User/Documents/GitHub/EProctor/face_recognition_data/classes.npy')

        faces_encodings = np.zeros((1, 128))
        no_of_faces = len(svc.predict_proba(faces_encodings)[0])
        count = dict()
        present = dict()
        log_time = dict()
        start = dict()
        for i in range(no_of_faces):
            count[encoder.inverse_transform([i])[0]] = 0
        # ---------------------------------------------------------
        im = show_image(cam, question)
        cv2.imshow('Liveness detection', im)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # <----------------------- ingest data
        # ret, im = cam.read()
        # im = imutils.resize(im, width=720)
        # im = cv2.flip(im, 1)
        gray_frame = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = detector(gray_frame, 0)
        # <----------------------- ingest data

        for i_try in range(limit_try):

            TOTAL_0 = TOTAL
            out_model = f_liveness_detection.detect_liveness(im, COUNTER, TOTAL_0)
            TOTAL = out_model['total_blinks']
            COUNTER = out_model['count_blinks_consecutive']
            dif_blink = TOTAL - TOTAL_0
            if dif_blink > 0:
                blinks_up = 1
            else:
                blinks_up = 0

            challenge_res = questions.challenge_result(question, out_model, blinks_up)

            im = show_image(cam, question)
            cv2.imshow('Liveness detection', im)

            for face in faces:
                (x, y, w, h) = face_utils.rect_to_bb(face)

                face_aligned = fa.align(im, gray_frame, face)
                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 1)
                # cv2.imshow('Liveness detection', im)

                (pred, prob) = predict(face_aligned, svc)

                if (pred != [-1]):
                    person_name = encoder.inverse_transform(np.ravel([pred]))[0]
                    pred = person_name
                    if count[pred] == 0:
                        count[pred] = count.get(pred, 0) + 1

                    # if count[pred] == 4 and (time.time() - start[pred]) > 1.2:
                    # count[pred] = 0
                    else:
                        # if count[pred] == 4 and (time.time()-start) <= 1.5:
                        present[pred] = True
                        # log_time[pred] = datetime.datetime.now()
                        count[pred] = count.get(pred, 0) + 1

                    # im = show_image(cam, str(person_name) + str(prob))
                    # cv2.imshow('Liveness detection', im)
                    cv2.putText(im, str(person_name) + str(prob), (x + 6, y + h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 0), 1)
                    cv2.imshow('Liveness detection', im)
                    user_name = str(person_name)
                    print(user_name)
                else:
                    person_name = "unknown"
                    user_name = person_name
                    cv2.putText(im, str(person_name), (x + 6, y + h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    print(user_name)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if challenge_res == "pass":

                im = show_image(cam, question + " : ok")
                cv2.imshow('Liveness detection', im)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                counter_ok_consecutives += 1
                if counter_ok_consecutives == limit_consecutives:
                    counter_ok_questions += 1
                    counter_try = 0
                    counter_ok_consecutives = 0
                    break
                else:
                    continue

            elif challenge_res == "fail":
                counter_try += 1
                show_image(cam, question + " : fail")

            elif i_try == limit_try - 1:
                break

        if counter_ok_questions == limit_questions:
            while True:
                im = show_image(cam, "LIVENESS SUCCESSFUL", color=(0, 255, 0))
                cv2.imshow('Liveness detection', im)
                print("SUCCESSFUL STUDENT IDENTITY AND LIVENESS VERIFICATION")
                liveTest = True
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #cv2.waitKey(1)
                break
        elif i_try == limit_try - 1:
            while True:
                im = show_image(cam, "LIVENESS FAIL")
                cv2.imshow('Liveness detection', im)
                print("UNSUCCESSFUL VERIFICATION")
                liveTest = False
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #cv2.waitKey(1)
                break
            break

    cam.release()
    #cam.stop()
    # destroying all the windows
    cv2.destroyAllWindows()
    #cv2.destroyWindow("shown_img")
    # update_attendance_in_db_in(present)

    if user_name == request.user.username:
        if liveTest:
            return redirect('successful_verification', id=id)
        else:
            messages.error(request, "Unsuccessful user liveness verification")
            return redirect('verification_before_exam', id=id)

    else:
        messages.error(request, "Unsuccessful student identity verification")
        return redirect('verification_before_exam', id=id)



# def verification_exam(request, id):
#     global person_name
#     detector = dlib.get_frontal_face_detector()
#
#     predictor = dlib.shape_predictor(
#         'C:/Users/User/Documents/GitHub/EProctor/face_recognition_data/shape_predictor_68_face_landmarks.dat')  # Add path to the shape predictor ######CHANGE TO RELATIVE PATH LATER
#     svc_save_path = "C:/Users/User/Documents/GitHub/EProctor/face_recognition_data/svc.sav"
#
#     with open(svc_save_path, 'rb') as f:
#         svc = pickle.load(f)
#     fa = FaceAligner(predictor, desiredFaceWidth=96)
#     encoder = LabelEncoder()
#     encoder.classes_ = np.load('C:/Users/User/Documents/GitHub/EProctor/face_recognition_data/classes.npy')
#
#     faces_encodings = np.zeros((1, 128))
#     no_of_faces = len(svc.predict_proba(faces_encodings)[0])
#     count = dict()
#     present = dict()
#     log_time = dict()
#     start = dict()
#     for i in range(no_of_faces):
#         count[encoder.inverse_transform([i])[0]] = 0
#         present[encoder.inverse_transform([i])[0]] = False
#
#     vs = VideoStream(src=0).start()
#
#     sampleNum = 0
#
#     while (True):
#         frame = vs.read()
#         frame = imutils.resize(frame, width=800)
#
#         gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = detector(gray_frame, 0)
#         start_time = time.time()
#         for face in faces:
#
#             print("INFO : inside for loop")
#             (x, y, w, h) = face_utils.rect_to_bb(face)
#
#             face_aligned = fa.align(frame, gray_frame, face)
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
#
#             (pred, prob) = predict(face_aligned, svc)
#
#             if (pred != [-1]):
#
#                 person_name = encoder.inverse_transform(np.ravel([pred]))[0]
#                 pred = person_name
#                 if count[pred] == 0:
#                     # start_time = time.time()
#                     start[pred] = time.time()
#                     count[pred] = count.get(pred, 0) + 1
#
#                 if count[pred] == 4 and (time.time() - start[pred]) > 1.2:
#                     count[pred] = 0
#                 else:
#                     # if count[pred] == 4 and (time.time()-start) <= 1.5:
#                     present[pred] = True
#                     # log_time[pred] = datetime.datetime.now()
#                     count[pred] = count.get(pred, 0) + 1
#                     print(pred, present[pred], count[pred])
#                 cv2.putText(frame, str(person_name) + str(prob), (x + 6, y + h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
#                             (0, 255, 0), 1)
#                 user_name = str(person_name)
#             else:
#                 person_name = "unknown"
#                 cv2.putText(frame, str(person_name), (x + 6, y + h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
#
#             cv2.imshow("Identity Verification", frame)
#             # timeRun = float(time.time() - start_time)
#             # while float(time.time() - start_time) < 10.0:
#             #     cv2.imshow("Identity Verification", frame)
#             # break
#
#         # if user_name == request.user.username:
#         #     messages.success(request, "Student identity verified successfully")
#         #     break
#         # else:
#         #     messages.error(request, "Invalid student")
#         #     break
#
#         # cv2.putText()
#         # Before continuing to the next loop, I want to give it a little pause
#         # waitKey of 100 millisecond
#         # cv2.waitKey(50)
#
#         # Showing the image in another window
#         # Creates a window with window name "Face" and with the image img
#
#         # Before closing it we need to give a wait command, otherwise the open cv wont work
#         # @params with the millisecond of delay 1
#         # cv2.waitKey(1)
#         # To get out of the loop
#
#         key = cv2.waitKey(50) & 0xFF
#         if (key == ord("q")):
#             break
#
#     # Stoping the videostream
#     vs.stop()
#
#     # destroying all the windows
#     cv2.destroyAllWindows()
#     # update_attendance_in_db_in(present)
#
#     if user_name == request.user.username:
#         return redirect('successful_verification', id=id)
#
#     else:
#         messages.error(request, "Invalid student")
#         return redirect('verification_before_exam', id=id)
