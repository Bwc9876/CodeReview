# Generated by Django 3.2.9 on 2021-11-01 20:58

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Rubric",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The name the students will use to pick a rubric when requesting a review",
                        max_length=20,
                    ),
                ),
                ("max_score", models.FloatField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="RubricCell",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("description", models.TextField()),
                ("score", models.FloatField()),
                ("index", models.SmallIntegerField()),
            ],
            options={
                "ordering": ["index"],
            },
        ),
        migrations.CreateModel(
            name="RubricRow",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=20)),
                ("description", models.TextField()),
                ("max_score", models.FloatField()),
                ("index", models.SmallIntegerField()),
            ],
            options={
                "ordering": ["index"],
            },
        ),
        migrations.CreateModel(
            name="ScoredRow",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("score", models.FloatField()),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
