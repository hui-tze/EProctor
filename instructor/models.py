from django.db import models
from django.contrib.auth.models import User


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    instructorEmail = models.CharField(max_length=100)
    instructorIC = models.CharField(max_length=12, null=False)
    instructorContact = models.CharField(max_length=11, null=False)
    instructorAddress = models.CharField(max_length=300, null=False)
    status = models.BooleanField(default=False)

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_instance(self):
        return self

    def __str__(self):
        return self.user.first_name
