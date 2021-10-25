"""
    This file defines additional tags and filters templates can call for Rubrics
"""

from django import template
from django.db.models import QuerySet

from Instructor.models import Rubric, RubricRow, RubricCell
from Main.models import Review

register = template.Library()


@register.filter(name="rows")
def get_rows(rubric: Rubric) -> QuerySet:
    """
        This filter gets the rows in a `Rubric`

        :param rubric: The rubric we want to get the rows of
        :type rubric: Rubric
        :return: A QuerySet with the rows of the Rubric
        :rtype: QuerySet
    """

    return RubricRow.objects.filter(parent_rubric=rubric)


@register.filter(name="cells")
def get_cells(row: RubricRow) -> QuerySet:
    """
        This filter gets the cells in a `RubricRow`

        :param row: The row to get the cells from
        :type row: RubricRow
        :return: The cells inside the row
        :rtype: QuerySet
    """

    return RubricCell.objects.filter(parent_row=row)


@register.filter(name='colspan')
def get_colspan(rubric: Rubric) -> int:
    """
        This filter gets the colspan needed to represent a Rubric as a table
        :param rubric: The rubric to check
        :type rubric: Rubric
        :returns: The colspan needed for the "scores" th element in the table
        :rtype: int
    """

    return max([RubricCell.objects.filter(parent_row=row).count()
                for row in RubricRow.objects.filter(parent_rubric=rubric)])


@register.filter(name='is_score')
def is_score(cell: RubricCell, review: Review):
    """
        This filter checks if a Cell has the score that a Reviewer selected

        :param cell: The cell to check the score of
        :type cell: RubricCell
        :param review: The Review to check the cell against
        :type review: Review
        :returns: Whether the Cell is the one that the Reviewer selected when grading the Review
        :rtype: bool
    """

    return cell.score == review.scoredrow_set.get(source_row=cell.parent_row).score


@register.filter(name="no_score")
def no_score(row: RubricRow, review: Review):
    """
        This filter checks if a row has no score (N/A) selected

        :param row: The row to check the score of
        :type row: RubricRow
        :param review: The Review to check the row against
        :type review: Review
        :returns: Whether the Row has no score selected
        :rtype: bool
    """

    return -1 == review.scoredrow_set.get(source_row=row).score
