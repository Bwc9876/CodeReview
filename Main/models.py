from json import JSONDecoder, JSONEncoder
from typing import Optional, Union
from uuid import uuid4, UUID

from django.db import models

from Users.models import User


def val_uuid(src: Union[str, UUID]) -> Optional[UUID]:
    try:
        return UUID(src) if type(src) == str else src
    except ValueError:
        return None


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True

    @classmethod
    def max_length(cls, field_name: str) -> int:
        return cls._meta.get_field(field_name).max_length


class RubricCell(BaseModel):
    description = models.TextField()
    score = models.FloatField()
    parent_row = models.ForeignKey('RubricRow', on_delete=models.CASCADE)
    index = models.SmallIntegerField()

    class Meta:
        ordering = ['index']


class RubricRow(BaseModel):
    name = models.CharField(max_length=20)
    description = models.TextField()
    max_score = models.FloatField()
    parent_rubric = models.ForeignKey('Rubric', on_delete=models.CASCADE)
    index = models.SmallIntegerField()

    class Meta:
        ordering = ['index']


class ScoredRow(BaseModel):
    parent_review = models.ForeignKey('Review', on_delete=models.CASCADE)
    source_row = models.ForeignKey('RubricRow', on_delete=models.CASCADE)
    score = models.FloatField()


class Rubric(BaseModel):
    name = models.CharField(max_length=20)
    max_score = models.FloatField()

    def to_json(self) -> str:
        new_obj = []

        for row in list(self.rubricrow_set.all()):
            new_row = {'name': row.name, 'description': row.description, 'cells': []}
            [new_row['cells'].append({'score': float(cell.score), 'description': cell.description})
             for cell in list(row.rubriccell_set.all())]
            new_obj.append(new_row)

        return JSONEncoder().encode(new_obj)

    def __str__(self) -> str:
        return self.name


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
    additional_comments = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"Review from {str(self.student)}"

    def score_fraction(self):
        my_score = 0
        max_score = self.rubric.max_score
        for scoredRow in self.scoredrow_set.all():
            if scoredRow.score == -1:
                max_score -= scoredRow.source_row.max_score
            else:
                my_score += scoredRow.score
        return f'{my_score}/{max_score}'

    def get_status(self):
        return Review.Status.labels[self.status]

    def affiliated(self, user):
        return self.student == user or (self.reviewer is not None and self.reviewer == user) or user.is_superuser
