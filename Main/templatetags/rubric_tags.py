from typing import List

from django import template

from Instructor.models import Rubric, RubricRow, RubricCell
from Main.models import Review

register = template.Library()


@register.filter(name="rows")
def get_rows(rubric: Rubric) -> List[RubricRow]:
    return RubricRow.objects.filter(parent_rubric=rubric)


@register.filter(name="cells")
def get_cells(row: RubricRow) -> List[RubricCell]:
    return RubricCell.objects.filter(parent_row=row)


@register.filter(name='colspan')
def get_colspan(rubric: Rubric) -> int:
    return max([RubricCell.objects.filter(parent_row=row).count()
                for row in RubricRow.objects.filter(parent_rubric=rubric)])


@register.filter(name='is_score')
def is_score(cell: RubricCell, review: Review):
    return cell.score == review.scoredrow_set.get(source_row=cell.parent_row).score


@register.filter(name="no_score")
def no_score(row: RubricRow, review: Review):
    return -1 == review.scoredrow_set.get(source_row=row).score
