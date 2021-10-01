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


class RubricCell(BaseModel):
    description = models.TextField()
    score = models.FloatField()
    parent_row = models.ForeignKey('RubricRow', on_delete=models.CASCADE)
    index = models.SmallIntegerField()

    class Meta:
        ordering = ['-score']


class RubricRow(BaseModel):
    name = models.CharField(max_length=20)
    description = models.TextField()
    max_score = models.FloatField()
    parent_rubric = models.ForeignKey('Rubric', on_delete=models.CASCADE)
    index = models.SmallIntegerField()


class Rubric(BaseModel):
    name = models.CharField(max_length=20)
    max_score = models.FloatField()

    @staticmethod
    def create_from_json(name: str, json: str, current_id: Optional[UUID] = None):
        new_rubric = Rubric.objects.get_or_create(id=current_id, defaults={'max_score': 0, 'name': name})[0]
        new_rubric.save()
        possible_points = 0

        new_obj = JSONDecoder().decode(json)

        for index, row in enumerate(new_obj.get("rows", [])):
            new_row, created = RubricRow.objects.get_or_create(parent_rubric=new_rubric, index=index, defaults={
                'name': row.get('name'),
                'description': row.get('description'),
                'index': index,
                'parent_rubric': new_rubric,
                'max_score': 0
            })
            if not created:
                new_row.name = row.get('name')
                new_row.description = row.get('description')
                new_row.max_score = 0
            new_row.save()
            for cell_index, cell in enumerate(row.get("cells", [])):
                score = int(cell.get("score"))
                new_row.max_score = max(score, new_row.max_score)
                new_cell, cell_created = RubricCell.objects.get_or_create(parent_row=new_row, index=cell_index,
                                                                          defaults={
                                                                              'description': cell.get("description"),
                                                                              'score': score,
                                                                              'parent_row': new_row,
                                                                              'index': cell_index
                                                                          })
                if not cell_created:
                    new_cell.description = cell.get('description')
                    new_cell.score = score
                new_cell.save()
            possible_points += new_row.max_score
            new_row.save()

            RubricCell.objects.filter(index__gt=len(row.get("cells", [])) - 1).delete()

        RubricRow.objects.filter(index__gt=len(new_obj.get("rows", [])) - 1).delete()

        new_rubric.max_score = possible_points
        new_rubric.save()
        return new_rubric

    def to_json(self) -> str:
        new_obj = {'rows': []}

        for row in list(self.rubricrow_set.all()):
            new_row = {'name': row.name, 'description': row.description, 'cells': []}
            [new_row['cells'].append({'score': cell.score, 'description': cell.description})
             for cell in list(row.rubriccell_set.all())]
            new_obj['rows'].append(new_row)

        return JSONEncoder().encode(new_obj)


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
