from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from .models import Subject


# Create your views here.

def question(request):
    all_subject = Subject.objects.all()
    context = {
        'all_subject': all_subject
    }
    return render(request, 'questionbank.html', context)


def subject(request):
    all_subject = Subject.objects.all()
    context = {
        'all_subject': all_subject
    }
    return render(request, 'subject.html', context)


def add_new_subject(request):
    all_subject = Subject.objects.all()
    context = {
        'all_subject': all_subject,
    }
    subject_code = request.POST["subject_code"]
    subject_name = request.POST["subject_name"]
    if Subject.objects.filter(subjectID=subject_code).exists():
        messages.warning(request, "Subject Code already Exists")
    else:
        subject_info = Subject(subjectID=subject_code, subjectName=subject_name)
        subject_info.save()
        messages.success(request, "Add Subject Successfully")
    return render(request, 'subject.html', context)


def validate_code(request):
    subject_code = request.GET.get('subject_code', None)
    data = {
        'is_taken': Subject.objects.filter(subjectID=subject_code).exists()
    }
    if data['is_taken']:
        data['error_message'] = "Subject Code already exists."
    return JsonResponse(data)



