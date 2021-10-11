from json import JSONEncoder

from django.db import models

from Main.models import BaseModel


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
    parent_review = models.ForeignKey('Main.Review', on_delete=models.CASCADE)
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
