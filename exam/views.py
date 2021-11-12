import time
from datetime import date, datetime, timedelta
import random

from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.base import ContentFile

from .models import *
from student.models import Student
from .forms import *
from django.http.response import StreamingHttpResponse, HttpResponse

from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import imutils
import cv2
import os
from django.conf import settings

import io
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors

face_detection_videocam = cv2.CascadeClassifier(os.path.join(
    settings.BASE_DIR, 'opencv_haarcascade_data/haarcascade_frontalface_default.xml'))
face_detection_webcam = cv2.CascadeClassifier(os.path.join(
    settings.BASE_DIR, 'opencv_haarcascade_data/haarcascade_frontalface_default.xml'))
# load our serialized face detector model from disk
prototxtPath = os.path.sep.join([settings.BASE_DIR, "face_detector/deploy.prototxt"])
weightsPath = os.path.sep.join([settings.BASE_DIR, "face_detector/res10_300x300_ssd_iter_140000.caffemodel"])
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)
maskNet = load_model(os.path.join(settings.BASE_DIR, 'face_detector/mask_detector.model'))
UPLOAD_FOLDER = '/static/snapshot/'
SNAPSHOT_FOLDER = os.path.join('static', 'snapshot')


# Create your views here.
def home(request):
    return render(request, 'index.html')


def question(request, pk):
    all_questions = Question.objects.filter(subject=pk)

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
    all_subjects = Subject.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(all_subjects, 5)
    try:
        all_subject = paginator.page(page)
    except PageNotAnInteger:
        all_subject = paginator.page(1)
    except EmptyPage:
        all_subject = paginator.page(paginator.num_pages)
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
    return render(request, 'subjects/subjectForm.html', {'form': form, 'edit': True})


def delete_subject(request, pk):
    sub = Subject.objects.get(subjectID=pk)
    sub.delete()
    return redirect('/exam/subject')


def subject_question(request):
    all_subject = Subject.objects.all()
    count = Subject.objects.all().count()
    i = 0
    ques = []
    for s in all_subject:
        ques.append(Question.objects.filter(subject=s.subjectID).count())
    context = {
        'all_subject': all_subject,
        'ques': ques,
        'count': count
    }
    return render(request, 'questions/subjectQuestion.html', context)


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
        return redirect('/exam/subject_question')
    return render(request, 'questions/questionForm.html', context)


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
        return redirect('/exam/subject_question')
    else:
        return render(request, 'questions/questionForm.html', context)
    return render(request, 'questions/questionForm.html', context)


def check_exam():
    all_exam = Exam.objects.filter(status='A')
    for t in all_exam:
        dt = datetime.combine(t.examDate, t.endTime)
        now = datetime.now()
        c = dt - now
        minutes = c.total_seconds() / 60
        if minutes < 0:
            Exam.objects.filter(examID=t.examID).update(status='I')
            exam = Exam.objects.filter(examID=t.examID)
            all_students = StudentExam.objects.filter(examID=t.examID)
            for s in all_students:
                correct = 0
                attempt = 0
                score = 0
                GPA = 0
                grade = ''
                student_ans = StudentAnswer.objects.filter(sdID=s.sdID)
                for ans in student_ans:
                    if ans.studAns is not None:
                        attempt += 1
                        correctAns = Answer.objects.filter(answerID=ans.studAns)
                        for c in correctAns:
                            if c.rightAns == 'T':
                                correct += 1
                for e in exam:
                    score = correct / e.quesNum * 100
                    if score > 80:
                        GPA = 4.0
                        grade = 'A'
                    elif score > 75:
                        GPA = 3.67
                        grade = 'A-'
                    elif score > 70:
                        GPA = 3.33
                        grade = 'B+'
                    elif score > 65:
                        GPA = 3.00
                        grade = 'B'
                    elif score > 60:
                        GPA = 2.67
                        grade = 'B-'
                    elif score > 55:
                        GPA = 2.33
                        grade = 'C+'
                    elif score > 50:
                        GPA = 2.00
                        grade = 'C'
                    elif score > 45:
                        GPA = 1.67
                        grade = 'C-'
                    elif score > 40:
                        GPA = 1.33
                        grade = 'D+'
                    elif score > 35:
                        GPA = 1.00
                        grade = 'D'
                    else:
                        GPA = 0.00
                        grade = 'F'
                if score >= 50:
                    status = 'P'
                else:
                    status = 'F'
                result_info = Result(studentID=s.studentID, examID=t.examID, ansAttempt=attempt, correctAns=correct,
                                     GPA=GPA, grade=grade, status=status)
                result_info.save()


def subject_exam(request):
    check_exam()
    all_subject = Subject.objects.all()
    i = 0
    exam = []
    for s in all_subject:
        exam.append(Exam.objects.filter(subject=s.subjectID, status='A').count())
    ques = []
    for s in all_subject:
        ques.append(Question.objects.filter(subject=s.subjectID).count())
    context = {
        'all_subject': all_subject,
        'exam': exam,
        'ques': ques
    }
    return render(request, 'examination/subjectExam.html', context)


def examination(request):
    all_exams = Exam.objects.filter(status='A')
    all_subject = Subject.objects.all()

    if request.GET.get('subject'):
        sub = request.GET.get('subject')
        all_exams = all_exams.filter(subject=sub)
    if request.GET.get('date'):
        dat = request.GET.get('date')
        all_exams = all_exams.filter(examDate=dat)

    context = {
        'all_exam': all_exams,
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
        start = examDate + ' ' + startTime
        end = examDate + ' ' + endTime
        st = datetime.strptime(start, "%Y-%m-%d %H:%M")
        et = datetime.strptime(end, "%Y-%m-%d %H:%M")
        c = et - st
        minutes = c.total_seconds() / 60
        exam_info = Exam(subject=sub, examDate=examDate, startTime=startTime, duration=minutes,
                         endTime=endTime, quesNum=quesNum, status='A')
        exam_info.save()
        messages.success(request, "Add Examination Successfully")
        return redirect('/exam/examination')
    return render(request, 'examination/examinationForm.html', context)


def edit_examination(request, pk):
    all_subject = Subject.objects.all()
    edit_exam = Exam.objects.get(examID=pk)
    context = {
        'all_subject': all_subject,
        'editExam': edit_exam
    }
    if request.method == 'POST':
        today = date.today()
        d1 = today.strftime("%Y%m%d")
        sub = request.POST["subject"]
        examDate = request.POST["date"]
        startTime = request.POST["stime"]
        endTime = request.POST["etime"]
        quesNum = request.POST["num"]
        start = examDate + ' ' + startTime
        end = examDate + ' ' + endTime
        st = datetime.strptime(start, "%Y-%m-%d %H:%M")
        et = datetime.strptime(end, "%Y-%m-%d %H:%M")
        c = et - st
        minutes = c.total_seconds() / 60
        Exam.objects.filter(examID=pk).update(subject=sub, examDate=examDate, startTime=startTime, duration=minutes,
                                              endTime=endTime, quesNum=quesNum, status='A')
        return redirect('/exam/examination')
    return render(request, 'examination/examinationForm.html', context)


def delete_examination(request, pk):
    exam = Exam.objects.get(examID=pk)
    exam.delete()
    return redirect('/exam/examination')


def my_examination(request, pk):
    check_exam()
    today = date.today()
    nextDay = date.today() + timedelta(days=1)
    today_exam = Exam.objects.filter(examDate=today, status='A')
    nextExam = Exam.objects.filter(status='A').filter(Q(examDate__gte=nextDay))
    student_exam = StudentExam.objects.filter(studentID=pk, status='P')
    i = 0
    j = 0
    for se in student_exam:
        print(se.examID)
        for e in today_exam:
            if e.examID == se.examID:
                i += 1

    for se in student_exam:
        print(se.examID)
        for e in nextExam:
            if e.examID == se.examID:
                j += 1

    context = {
        'total_exam': i,
        'upcoming': j,
        'pk': pk
    }
    return render(request, 'examination/studentExam.html', context)


def schedule_exam_list(request, pk):
    schedule_exam = StudentExam.objects.filter(studentID=pk, status='P')
    today = date.today()
    all_exams = Exam.objects.all()
    exam = all_exams.filter(examDate=today, status='A')
    all_subjects = Subject.objects.all()
    context = {
        'my_exam': schedule_exam,
        'all_exams': exam,
        'all_subjects': all_subjects
    }
    return render(request, 'examination/studentExamList.html', context)


def upcoming_exam_list(request, pk):
    upcoming_exam = StudentExam.objects.filter(studentID=pk)
    today = date.today() + timedelta(days=1)
    all_exams = Exam.objects.all()
    exam = all_exams.filter(status='A').filter(Q(examDate__gte=today))
    all_subjects = Subject.objects.all()
    context = {
        'my_exam': upcoming_exam,
        'all_exams': exam,
        'all_subjects': all_subjects,
        'upcoming': True
    }
    return render(request, 'examination/studentExamList.html', context)


def exam_rules(request, pk):
    exam = StudentExam.objects.filter(sdID=pk)
    for e in exam:
        exam_info = Exam.objects.filter(examID=e.examID)
    all_subjects = Subject.objects.all()
    if not StudentAnswer.objects.filter(sdID=pk).exists():
        for e in exam_info:
            all_questions = Question.objects.filter(subject=e.subject, status='A').order_by('?')[:e.quesNum]
        for ques in all_questions:
            ques_ans = StudentAnswer(questionID=ques.questionID, sdID=pk)
            ques_ans.save()

    context = {
        'exam_info': exam_info,
        'all_subjects': all_subjects,
        'pk': pk
    }
    return render(request, 'examination/examinationRules.html', context)


def start_exam(request, pk):
    exam = StudentExam.objects.filter(sdID=pk)
    for e in exam:
        exam_info = Exam.objects.filter(examID=e.examID)
    all_questions = Question.objects.all()
    student_question = StudentAnswer.objects.filter(sdID=pk)
    all_answer = Answer.objects.all()
    count = StudentAnswer.objects.filter(sdID=pk).count()
    for t in exam_info:
        sub = Subject.objects.get(subjectID=t.subject)
        dt = datetime.combine(t.examDate, t.endTime)
        timestamp = datetime.timestamp(dt) * 1000

    context = {
        'student_question': student_question,
        'all_questions': all_questions,
        'all_answer': all_answer,
        'count': count,
        'pk': pk,
        'exam_info': exam_info,
        'timestamp': timestamp,
        'subject': sub
    }

    return render(request, 'examination/startExam.html', context)


def finish_exam(request, pk):
    now = datetime.now()
    sid = StudentExam.objects.get(sdID=pk)
    stud = sid.studentID
    StudentExam.objects.filter(sdID=pk).update(status='E', endAttempt=now)
    return redirect('/exam/my_examination/' + str(request.user.id))


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


def get_max(request):
    if request.is_ajax():
        choice = request.POST.get('value', None)
        print(choice)
        count = Question.objects.filter(subject=choice).count()
        response = {  # response message
            'max': count
        }
        print(count)
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


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request, pk):
    return StreamingHttpResponse(gen(VideoCamera(pk)), content_type='multipart/x-mixed-replace; boundary=frame')


def snapshot(request, pk):
    return StreamingHttpResponse(gen(Snapshot(pk)), content_type='multipart/x-mixed-replace; boundary=frame')


def view_result(request):
    check_exam()
    all_subject = Subject.objects.all()
    all_exams = Exam.objects.filter(status='I')

    if request.GET.get('subject'):
        sub = request.GET.get('subject')
        all_exams = all_exams.filter(subject=sub)
    if request.GET.get('date'):
        dat = request.GET.get('date')
        all_exams = all_exams.filter(examDate=dat)

    context = {
        'all_subject': all_subject,
        'all_exam': all_exams,
        'result': True
    }
    return render(request, 'examination/examination.html', context)


def exam_result(request, pk):
    all_exam = Exam.objects.filter(subject=pk, status='I')
    all_subject = Subject.objects.all()
    context = {
        'all_exam': all_exam,
        'all_subject': all_subject,
        'result': True
    }
    return render(request, 'examination/examination.html', context)


def student_result_list(request, pk):
    all_result = Result.objects.filter(examID=pk)
    all_student = Student.objects.all()
    context = {
        'all_result': all_result,
        'all_student': all_student,
        'pk': pk
    }
    return render(request, 'examination/studentResultList.html', context)


def view_snapshot(request, sid, eid):
    sdID = StudentExam.objects.filter(studentID=sid, examID=eid)
    exam_info = Exam.objects.filter(examID=eid)
    for s in exam_info:
        subject_info = Subject.objects.filter(subjectID=s.subject)
    for s in sdID:
        snap = Snapshot.objects.filter(sdID=sid, examID=eid)
    context = {
        'exam_info': exam_info,
        'subject_info': subject_info,
        'snapshot': snap,
        'type1': 1,
        'type2': 2,
        'type3': 3
    }
    return render(request, 'examination/viewSnapshot.html', context)


def view_result_paper(request, sid, eid):
    sdID = StudentExam.objects.filter(studentID=sid, examID=eid)
    exam_info = Exam.objects.filter(examID=eid)
    for s in exam_info:
        subject_info = Subject.objects.filter(subjectID=s.subject)
    for s in sdID:
        student_question = StudentAnswer.objects.filter(sdID=s.sdID)
    all_questions = Question.objects.all()
    all_answer = Answer.objects.all()
    context = {
        'exam_info': exam_info,
        'subject_info': subject_info,
        'student_question': student_question,
        'all_questions': all_questions,
        'all_answer': all_answer,
        'instructor': True
    }
    return render(request, 'examination/questionPaper.html', context)


def my_result(request, pk):
    check_exam()
    student_exam = StudentExam.objects.filter(studentID=pk)
    all_exams = Exam.objects.filter(status='I')
    all_subjects = Subject.objects.all()
    context = {
        'my_exam': student_exam,
        'all_exams': all_exams,
        'all_subjects': all_subjects
    }
    return render(request, 'examination/myResult.html', context)


def student_answer(request, pk):
    student_exam = StudentExam.objects.filter(sdID=pk)
    for e in student_exam:
        exam_info = Exam.objects.filter(examID=e.examID)
        result = Result.objects.filter(studentID=e.studentID, examID=e.examID)
    for s in exam_info:
        subject_info = Subject.objects.filter(subjectID=s.subject)
    student_question = StudentAnswer.objects.filter(sdID=pk)
    all_questions = Question.objects.all()
    all_answer = Answer.objects.all()
    context = {
        'my_exam': student_exam,
        'exam_info': exam_info,
        'subject_info': subject_info,
        'student_question': student_question,
        'all_questions': all_questions,
        'all_answer': all_answer,
        'result': result,
        'pk': pk
    }
    return render(request, 'examination/studentAnswer.html', context)


def result_paper(request, pk):
    student_exam = StudentExam.objects.filter(sdID=pk)
    for e in student_exam:
        exam_info = Exam.objects.filter(examID=e.examID)
        result = Result.objects.filter(studentID=e.studentID, examID=e.examID)
    for s in exam_info:
        subject_info = Subject.objects.filter(subjectID=s.subject)
    student_question = StudentAnswer.objects.filter(sdID=pk)
    all_questions = Question.objects.all()
    all_answer = Answer.objects.all()
    context = {
        'my_exam': student_exam,
        'exam_info': exam_info,
        'subject_info': subject_info,
        'student_question': student_question,
        'all_questions': all_questions,
        'all_answer': all_answer,
        'result': result
    }
    return render(request, 'examination/questionPaper.html', context)


def student_result_paper(request, pk):
    student_exam = StudentExam.objects.filter(sdID=pk)
    for e in student_exam:
        exam_info = Exam.objects.filter(examID=e.examID)
        result = Result.objects.filter(studentID=e.studentID, examID=e.examID)
    for s in exam_info:
        subject_info = Subject.objects.filter(subjectID=s.subject)
    student_question = StudentAnswer.objects.filter(sdID=pk)
    all_questions = Question.objects.all()
    all_answer = Answer.objects.all()
    context = {
        'my_exam': student_exam,
        'exam_info': exam_info,
        'subject_info': subject_info,
        'student_question': student_question,
        'all_questions': all_questions,
        'all_answer': all_answer,
        'result': result
    }
    return render(request, 'examination/studentPaper.html', context)


def report(request):
    check_exam()
    all_subject = Subject.objects.all()
    all_exams = Exam.objects.filter(status='I')

    if request.GET.get('subject'):
        sub = request.GET.get('subject')
        all_exams = all_exams.filter(subject=sub)
    if request.GET.get('date'):
        dat = request.GET.get('date')
        all_exams = all_exams.filter(examDate=dat)

    context = {
        'all_subject': all_subject,
        'all_exam': all_exams,
        'report': True
    }
    return render(request, 'examination/examination.html', context)


def report_view(request, pk):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer,
                            rightMargin=30,
                            leftMargin=30,
                            topMargin=30,
                            bottomMargin=30,
                            pagesize=A4)

    styles = getSampleStyleSheet()

    # Our container for 'Flowable' objects
    elements = []

    title_style = styles["Heading1"]

    # 0: left, 1: center, 2: right
    title_style.alignment = 1

    # creating the paragraph with
    # the heading text and passing the styles of it
    title = Paragraph("Student Result Report", title_style)

    # A large collection of style sheets pre-made for us
    styles.add(ParagraphStyle(name='RightAlign', fontName='Arial', alignment=TA_RIGHT))

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    exam = Exam.objects.filter(examID=pk)
    sub = Subject.objects.all()
    result = Result.objects.filter(examID=pk)
    student = Student.objects.all()

    for e in exam:
        for s in sub:
            if e.subject == s.subjectID:
                exam_data = [['Subject', s.subjectCode + " " + s.subjectName],
                             ['Exam Date', str(e.examDate)],
                             ['Time', str(e.startTime) + " - " + str(e.endTime)],
                             ['Duration', str(e.duration) + "minutes"]]
    exam_table = Table(exam_data, colWidths=[100, 300], hAlign='LEFT')

    # Need a place to store our table rows
    table_data = [["NO", "Name", "IC", "GPA", "Grade", "Status"]]
    for i, result in enumerate(result):
        for s in student:
            if result.studentID == s.user.id:
                # Add a row to the table
                if result.status == 'F':
                    res = "Fail"
                else:
                    res = "Pass"
                table_data.append(
                    [i + 1, s.user.first_name + " " + s.user.last_name, s.studentIC, result.GPA, result.grade,
                     res])

    # Create the table
    user_table = Table(table_data, colWidths=[30, 200, 100, 60, 60, 60], hAlign='LEFT')
    user_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                                    ('BOX', (0, 0), (-1, -1), 1, colors.black),
                                    ("GRID", (0, 0), (4, 4), 1, colors.black),
                                    ("BACKGROUND", (0, 0), (5, 0), colors.gray),
                                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                                    ]))

    exam_table.setStyle(TableStyle([('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                                    ('BOX', (0, 0), (-1, -1), 1, colors.black),
                                    ("GRID", (0, 0), (4, 4), 1, colors.black),
                                    ("BACKGROUND", (0, 0), (5, 0), colors.white),
                                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                                    ]))

    space = Paragraph("\n\n\n\n<br/>", title_style)
    elements.append(title)
    elements.append(exam_table)
    elements.append(space)
    elements.append(user_table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


global total
total = 0

global flag
flag = True


class VideoCamera(object):
    def __init__(self, pk):
        self.video = cv2.VideoCapture(0)
        self.i = 0
        self.x = pk

    def __del__(self):
        self.video.release()

    def get_frame(self):
        global total
        total += 1
        # print(total)
        success, image = self.video.read()

        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces_detected = face_detection_videocam.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        for (x, y, w, h) in faces_detected:
            cv2.rectangle(image, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
        frame_flip = cv2.flip(image, 1)
        if total % 2000 == 0:
            print("yes")
            se = StudentExam.objects.filter(sdID=self.x)
            for s in se:
                sid = s.studentID
                eid = s.examID
            count = Snapshot.objects.filter(examID=eid).count()
            print(count)
            filename = 'Snapshot' + str(eid) + str(count + 1) + '.jpg'
            cv2.imwrite(os.path.join(SNAPSHOT_FOLDER, filename), frame_flip)
            snap = Snapshot(sdID=sid, examID=eid, type=1, image=filename)
            snap.save()
        self.i += 1
        global flag
        # img_model = Snapshot(type=1, saID=1, time=datetime.now().time(), image=content)
        if len(faces_detected) <= 0:
            cv2.putText(frame_flip, 'FACE NOT FOUND!', (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2, cv2.LINE_4)
            cv2.copyMakeBorder(frame_flip, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=[0, 0, 255])
            if flag:
                flag = False
                se = StudentExam.objects.filter(sdID=self.x)
                for s in se:
                    sid = s.studentID
                    eid = s.examID
                count = Snapshot.objects.filter(examID=eid).count()
                print(count)
                filename = 'Snapshot' + str(eid) + str(count + 1) + '.jpg'
                cv2.imwrite(os.path.join(SNAPSHOT_FOLDER, filename), frame_flip)
                snap = Snapshot(sdID=sid, examID=eid, type=2, image=filename)
                snap.save()
        elif len(faces_detected) > 1:
            cv2.putText(frame_flip, 'EXTRA PEOPLE IN FRAME!', (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2,
                        cv2.LINE_4, False)
            if flag:
                flag = False
                se = StudentExam.objects.filter(sdID=self.x)
                for s in se:
                    sid = s.studentID
                    eid = s.examID
                count = Snapshot.objects.filter(examID=eid).count()
                filename = 'Snapshot' + str(eid) + str(count + 1) + '.jpg'
                cv2.imwrite(os.path.join(SNAPSHOT_FOLDER, filename), frame_flip)
                snap = Snapshot(sdID=sid, examID=eid, type=3, image=filename)
                snap.save()

        else:
            flag = True
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()
