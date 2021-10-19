from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    studentContact = models.CharField(max_length=11, null=False)
    studentAddress = models.CharField(max_length=300, null=False)
    studentEmail = models.CharField(max_length=100)
    studentGender = models.CharField(max_length=1, null=False)
    studentIC = models.CharField(max_length=12, null=False)
    studentDOB = models.DateField(null=False)

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_instance(self):
        return self

    def __str__(self):
        return self.user.first_name
