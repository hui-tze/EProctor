# Generated by Django 3.0.5 on 2021-10-19 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('answerID', models.AutoField(primary_key=True, serialize=False)),
                ('answerDesc', models.CharField(max_length=500)),
                ('question', models.CharField(max_length=20)),
                ('rightAns', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('examID', models.AutoField(primary_key=True, serialize=False)),
                ('examDate', models.DateField()),
                ('startTime', models.TimeField()),
                ('endTime', models.TimeField()),
                ('duration', models.FloatField()),
                ('subject', models.IntegerField()),
                ('quesNum', models.IntegerField()),
                ('status', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('questionID', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('questionDesc', models.CharField(max_length=500)),
                ('subject', models.IntegerField()),
                ('status', models.CharField(choices=[('A', 'Active'), ('I', 'Inactive')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('subjectID', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('subjectCode', models.CharField(max_length=12)),
                ('subjectName', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('saID', models.AutoField(primary_key=True, serialize=False)),
                ('questionID', models.CharField(max_length=20)),
                ('studAns', models.IntegerField(null=True)),
                ('sdID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='StudentExam',
            fields=[
                ('sdID', models.AutoField(primary_key=True, serialize=False)),
                ('examID', models.IntegerField()),
                ('studentID', models.IntegerField()),
                ('status', models.CharField(max_length=1, null=True)),
            ],
        ),
    ]
