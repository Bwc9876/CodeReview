# Generated by Django 3.2.9 on 2021-11-09 13:33

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('Users', '0002_user_student_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='student_id',
        ),
    ]