from json import JSONDecoder

from django.shortcuts import render

from . import models


def rubric_factory(raw_json):
    raw_dict = JSONDecoder().decode(raw_json)
    rubric_max = 0
    new_rubric = models.Rubric.objects.create(name=raw_dict["name"], max_score=0)
    new_rubric.save()
    for row in raw_dict["rows"]:
        row_max = 0
        new_row = models.RubricRow.objects.create(name=row["name"], description=row["description"], max_score=0,
                                                  parent_rubric=new_rubric)
        for cell in row["cells"]:
            if row_max < cell["score"]:
                row_max = cell["score"]
            new_cell = models.RubricCell.objects.create(description=cell["description"], score=cell["score"],
                                                        parent_row=new_row)
            new_cell.save()
        rubric_max += row_max
        new_row.max_score = row_max
        new_row.save()
    new_rubric.max_score = rubric_max
    new_rubric.save()
    return new_rubric


def home_view(request):
    return render(request, "home.html")
