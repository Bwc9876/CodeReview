from json import JSONDecoder, JSONDecodeError
from typing import List

from django.forms import Form, ModelForm, Field, TextInput
from django.forms.fields import CharField

from . import models


class CreateRubricWidget(TextInput):
    template_name = "widgets/create_rubric.html"

    class Media:
        css = {'all': ('css/rubrics/rubric_create.css',)}
        js = ('js/rubrics/rubric-create-widget.js',)


class CreateRubricField(Field):
    widget = CreateRubricWidget()


class GradeReviewWidget(TextInput):
    template_name = "widgets/rubric_grade.html"
    rubric = None

    class Media:
        css = {'all': ('css/rubrics/rubric_table.css',)}
        js = ('js/rubrics/rubric-grade-widget.js',)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['rubric'] = self.rubric
        return context


class RubricForm(ModelForm):
    rubric = CreateRubricField()

    class Meta:
        model = models.Rubric
        fields = ['name']

    def save(self, commit=True):
        new_rubric = super().save(commit=False)
        new_rubric.max_score = 0
        new_rubric.save()
        json = self.cleaned_data.get('rubric')
        possible_points = 0

        new_obj = JSONDecoder().decode(json)

        for index, row in enumerate(new_obj.get("rows", [])):
            new_row, created = models.RubricRow.objects.get_or_create(parent_rubric=new_rubric, index=index, defaults={
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
                new_cell, cell_created = models.RubricCell.objects.get_or_create(parent_row=new_row, index=cell_index,
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

            models.RubricCell.objects.filter(index__gt=len(row.get("cells", [])) - 1).delete()

        models.RubricRow.objects.filter(index__gt=len(new_obj.get("rows", [])) - 1).delete()

        new_rubric.max_score = possible_points
        new_rubric.save()
        return new_rubric

    def json_exit(self) -> None:
        self.add_error('rubric', "Invalid JSON")

    def clean(self) -> None:
        cleaned_data: dict = super().clean()
        raw_json: str = cleaned_data.get("rubric")

        if raw_json is not None:
            try:
                obj: dict = dict(JSONDecoder().decode(cleaned_data.get("rubric")))
                if "rows" in obj.keys():
                    rows = obj.get("rows")
                    if type(rows) == list:
                        for row in rows:
                            if type(row) == dict:
                                if "name" not in row.keys():
                                    self.json_exit()
                                    return
                                if "description" not in row.keys():
                                    self.json_exit()
                                    return
                                if "cells" in row.keys():
                                    cells = row.get("cells")
                                    if type(cells) == list:
                                        for cell in cells:
                                            if type(cell) == dict:
                                                if "description" not in cell.keys():
                                                    self.json_exit()
                                                    return
                                                if "score" in cell.keys():
                                                    try:
                                                        int(cell.get("score"))
                                                    except ValueError:
                                                        self.json_exit()
                                                        return
                                                else:
                                                    self.json_exit()
                                                    return
                                            else:
                                                self.json_exit()
                                                return
                                    else:
                                        self.json_exit()
                                        return
                                else:
                                    self.json_exit()
                                    return
                            else:
                                self.json_exit()
                                return
                    else:
                        self.json_exit()
                        return
                else:
                    self.json_exit()
                    return
            except JSONDecodeError:
                self.json_exit()


class CreateReviewForm(ModelForm):
    class Meta:
        model = models.Review
        fields = ['schoology_id', 'rubric']


class GradeReviewForm(ModelForm):
    scores = CharField(max_length=200, widget=GradeReviewWidget())

    class Meta:
        model = models.Review
        fields = ['additional_comments']

    def save(self, commit=True):
        new_review: models.Review = super(GradeReviewForm, self).save(commit=False)
        scores_array: List[str] = self.cleaned_data.get("scores").split(',')
        for i in range(len(scores_array)):
            score = float(scores_array[i])
            row = models.RubricRow.objects.get(parent_rubric=new_review.rubric, index=i)
            scored_row = models.ScoredRow.objects.create(source_row=row, parent_review=new_review, score=score)
            scored_row.save()
        if commit:
            new_review.save()
        return new_review

    field_order = ['scores', 'additional_comments']

    def set_rubric(self, rubric):
        self.fields['scores'].widget.rubric = rubric

    # TODO: Add validation
