"""
    This file defines additional tags and filters templates can call for Rubrics
"""

from django import template
from django.db.models import QuerySet

from Instructor.models import Rubric, RubricRow, RubricCell, ScoredRow
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


@register.filter(name="colspan")
def get_colspan(rubric: Rubric) -> int:
    """
    This filter gets the colspan needed to represent a Rubric as a table
    :param rubric: The rubric to check
    :type rubric: Rubric
    :returns: The colspan needed for the "scores" th element in the table
    :rtype: int
    """

    return max(
        [
            RubricCell.objects.filter(parent_row=row).count()
            for row in RubricRow.objects.filter(parent_rubric=rubric)
        ]
    )


@register.filter(name="get_scores")
def get_scores_as_json(review: Review, rubric: Rubric) -> str:
    """
    This function gets the scores for a `Review` as a JSON string

    :param review: The review to get the scores for
    :type review: Review
    :param rubric: The rubric to get the scores for
    :type rubric: Rubric
    :return: A JSON string representing the scores
    :rtype: str
    """

    scores = []
    for row in RubricRow.objects.filter(parent_rubric=rubric):
        try:
            scores.append(
                ScoredRow.objects.get(parent_review=review, source_row=row).score
            )
        except ScoredRow.DoesNotExist:
            scores.append(-1)
    return f"[{','.join([str(score) for score in scores])}]"


@register.filter(name="is_score")
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
