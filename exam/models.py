from django.db import models
from django import forms

# Create your models here.
class Subject(models.Model):
    subjectID = models.AutoField(primary_key=True, unique=True, null=False)
    subjectCode = models.CharField(max_length=12)
    subjectName = models.CharField(max_length=100)

    def __str__(self):
        return self.subjectCode + " " + self.subjectName


class Question(models.Model):
    STATUS = (
        ('A', 'Active'),
        ('I', 'Inactive'),
    )
    questionID = models.CharField(primary_key=True, max_length=20)
    questionDesc = models.CharField(max_length=500)
    subject = models.IntegerField()
    status = models.CharField(max_length=1, choices=STATUS)

    def __str__(self):
        return self.questionID


class Answer(models.Model):
    answerID = models.AutoField(primary_key=True)
    answerDesc = models.CharField(max_length=500)
    question = models.CharField(max_length=20)
    rightAns = models.CharField(max_length=1)

    def __str__(self):
        return self.answerID


class Exam(models.Model):
    examID = models.AutoField(primary_key=True)
    examDate = models.DateField()
    startTime = models.TimeField()
    endTime = models.TimeField()
    duration = models.FloatField()
    subject = models.IntegerField()
    quesNum = models.IntegerField()
    status = models.CharField(max_length=1)


class StudentExam(models.Model):
    sdID = models.AutoField(primary_key=True)
    examID = models.IntegerField()
    studentID = models.IntegerField()
    status = models.CharField(max_length=1, null=True)


class StudentAnswer(models.Model):
    saID = models.AutoField(primary_key=True)
    questionID = models.CharField(max_length=20)
    studAns = models.IntegerField(null=True)
    sdID = models.IntegerField()


