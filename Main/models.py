from uuid import uuid4

from django.db import models

from Users.models import User


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class Rubric(BaseModel):
    name = models.CharField(max_length=20)
    max_score = models.FloatField()


class RubricRow(BaseModel):
    name = models.CharField(max_length=20)
    description = models.TextField()
    max_score = models.FloatField()
    parent_rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE)


class RubricCell(BaseModel):
    description = models.TextField()
    score = models.FloatField()
    parent_row = models.ForeignKey(RubricRow, on_delete=models.CASCADE)


class Review(BaseModel):

    class Status(models.TextChoices):
        OPEN = 0, "Open"
        ASSIGNED = 1, "Taken"
        CLOSED = 2, "Completed"

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer", null=True)
    schoology_id = models.CharField(max_length=10, null=True)
    status = models.IntegerField(choices=Status.choices, default=Status.OPEN)
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, related_name="source_rubric")
    scores = models.CharField(default="", max_length=100)
    additional_comments = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)
