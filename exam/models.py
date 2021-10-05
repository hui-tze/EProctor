from django.db import models


# Create your models here.
class Subject(models.Model):
    subjectID = models.CharField(max_length=12, primary_key=True)
    subjectName = models.CharField(max_length=100)

    def __str__(self):
        return self.subjectID + ' - ' + self.subjectName


