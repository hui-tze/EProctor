from datetime import date, datetime

from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from .filters import QuestionFilter

from .models import *
from student.models import Student
from .forms import *
import cv2
import sys
from django.http.response import StreamingHttpResponse
from exam.camera import VideoCamera, IPWebCam, MaskDetect, LiveWebCam


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
        timestamp = datetime.timestamp(dt)*1000
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


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
    return StreamingHttpResponse(gen(VideoCamera()), content_type='multipart/x-mixed-replace; boundary=frame')


def webcam_feed(request):
    return StreamingHttpResponse(gen(IPWebCam()), content_type='multipart/x-mixed-replace; boundary=frame')
