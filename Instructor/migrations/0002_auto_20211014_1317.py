# Generated by Django 3.2.8 on 2021-10-14 13:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('Instructor', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='rubriccell',
            unique_together={('parent_row', 'index')},
        ),
        migrations.AlterUniqueTogether(
            name='rubricrow',
            unique_together={('parent_rubric', 'index')},
        ),
    ]