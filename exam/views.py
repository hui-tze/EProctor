from datetime import date

from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from .filters import QuestionFilter

from .models import *
from .forms import *


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
    form = ExamForm(request.POST)
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


def my_examination(request):
    all_questions = Question.objects.all()
    all_answer = Answer.objects.all()
    count = Question.objects.all().count()
    page = request.GET.get('page', 1)
    paginator = Paginator(all_questions, 1)
    try:
        all_question = paginator.page(page)
    except PageNotAnInteger:
        all_question = paginator.page(1)
    except EmptyPage:
        all_question = paginator.page(paginator.num_pages)

    context = {
        'all_question': all_question,
        'all_answer': all_answer,
        'count': count
    }
    return render(request, 'examination/startExam.html', context)