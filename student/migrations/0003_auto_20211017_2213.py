# Generated by Django 3.0.5 on 2021-10-17 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_auto_20211015_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='studentContact',
            field=models.CharField(max_length=11),
        ),
    ]