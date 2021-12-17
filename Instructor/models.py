"""
    This file defines models that will be converted to tables in the database for the Instructor app
"""

from json import JSONEncoder

from django.db import models

from Main.models import BaseModel


class RubricCell(BaseModel):
    """
        This model is used to represent a cell in a rubric in the database

        :cvar score: The score the student will receive
        :cvar description: The description of the cell, what the student has to do to get this score
        :cvar parent_row: The `RubricRow` object that this cell is in
        :cvar index: The position of this cell in a `RubricRow`
    """

    description = models.TextField()
    score = models.FloatField()
    parent_row = models.ForeignKey('RubricRow', on_delete=models.CASCADE)
    index = models.SmallIntegerField()

    class Meta:
        """
            This internal class defines how the model will function in the database

            :cvar ordering: We order the cells by their index
            :cvar unique_together: We don't want two cells at the same position on a row,
             so we make `RubricCell.parent_row` and `RubricCell.index` unique together
        """

        ordering = ['index']
        unique_together = (('parent_row', 'index'),)


class RubricRow(BaseModel):
    """
        This model represents a row in a rubric in the database

        :cvar name: The name of the row
        :cvar description: The description of the row
        :cvar max_score: The max score a row can have
        :cvar parent_rubric: The `Rubric` that this row is inside
        :cvar index: The position of this row in the rubric
    """

    name = models.CharField(max_length=20)
    description = models.TextField()
    max_score = models.FloatField()
    parent_rubric = models.ForeignKey('Rubric', on_delete=models.CASCADE)
    index = models.SmallIntegerField()

    class Meta:
        """
            This internal class defines how the model will function in the database

            :cvar ordering: Rows should be ordered by their index
            :cvar unique_together: We don't want two rows at the same position on a rubric,
             so we make `RubricRow.parent_rubric` and `RubricRow.index` unique together
        """

        ordering = ['index']
        unique_together = (('parent_rubric', 'index'),)


class ScoredRow(BaseModel):
    """
        This model represents a row that has been graded by a reviewer in the database

        :cvar parent_review: The review that this score belongs to
        :cvar source_row: The row that has been scored
        :cvar score: The score that was put in by the reviewer
    """

    parent_review = models.ForeignKey('Main.Review', on_delete=models.CASCADE)
    source_row = models.ForeignKey('RubricRow', on_delete=models.CASCADE)
    score = models.FloatField()


class Rubric(BaseModel):
    """
        This model represents a Rubric in the database

        :cvar name: The name of the rubric
        :cvar max_score: The max possible score that a student can get with this rubric
    """

    name = models.CharField(max_length=20,
                            help_text="The name the students will use to pick a rubric when requesting a review")
    max_score = models.FloatField()

    def to_json(self) -> str:
        """
            This function converts the Rubric to json for use in the front-end

            :returns: A JSON representation of this rubric
            :rtype: str
        """

        new_obj = []

        for row in list(self.rubricrow_set.select_related()):
            new_row = {'name': row.name, 'description': row.description, 'cells': []}
            [new_row['cells'].append({'score': float(cell.score), 'description': cell.description})
             for cell in list(row.rubriccell_set.all())]
            new_obj.append(new_row)

        return JSONEncoder().encode(new_obj)

    def __str__(self) -> str:
        """
            This function defines how this object is cast to a string

            :returns: The name of the Rubric
            :rtype: str
        """

        return self.name
