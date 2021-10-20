from json import JSONDecoder, JSONDecodeError
from typing import List

from django.forms import ModelForm, TextInput, Textarea
from django.forms.fields import CharField
from jsonschema.validators import Draft202012Validator

from Instructor.models import RubricRow, ScoredRow
from . import models


class GradeReviewWidget(TextInput):
    template_name = "widgets/rubric_grade.html"
    input_type = 'hidden'
    rubric = None

    class Media:
        css = {'all': ('css/rubrics/rubric_table.css',)}
        js = ('js/rubrics/rubric-grade-widget.js',)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['rubric'] = self.rubric
        return context


class CreateReviewForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Review
        fields = ['schoology_id', 'rubric']

    def save(self, commit=True):
        new_review: models.Review = super().save(commit=False)
        new_review.student = self.user
        if commit:
            new_review.save()
        return new_review


class GradeReviewForm(ModelForm):
    scores = CharField(max_length=200, widget=GradeReviewWidget(), help_text="Please fill out each row in the rubric.  If a row does not apply to this specific assignment, select \"N/A\"")

    _validation_schema = {
        "type": "array",
        "items": {
            "type": "number",
            "minimum": -1
        }
    }

    def __init__(self, *args, **kwargs):
        instance: models.Review = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        if instance:
            self.rubric = instance.rubric
            self.fields['scores'].widget.rubric = self.rubric
        else:
            raise ValueError("An instance must be provided to GradeReviewForm!")
        target_item_length = self.rubric.rubricrow_set.count()
        self._validation_schema['maxItems'] = target_item_length
        self._validation_schema['minItems'] = target_item_length
        self._json_validator = Draft202012Validator(self._validation_schema)

    class Meta:
        model = models.Review
        fields = ['additional_comments']
        widgets = {
            'additional_comments': Textarea(attrs={"style": "height: 150px;"})
        }

    def save(self, commit=True):
        new_review: models.Review = super(GradeReviewForm, self).save(commit=False)
        scores_array: List[str] = JSONDecoder().decode(self.cleaned_data.get('scores'))
        for i in range(len(scores_array)):
            score = float(scores_array[i])
            row = RubricRow.objects.get(parent_rubric=new_review.rubric, index=i)
            scored_row = ScoredRow.objects.create(source_row=row, parent_review=new_review, score=score)
            scored_row.save()
        new_review.status = models.Review.Status.CLOSED
        if commit:
            new_review.save()
        return new_review

    field_order = ['scores', 'additional_comments']

    def clean(self):
        cleaned_data: dict = super(GradeReviewForm, self).clean()
        scores_json: str = cleaned_data.get('scores')

        if scores_json:
            try:
                errors = sorted(self._json_validator.iter_errors(JSONDecoder().decode(scores_json)), key=str)
                [self.add_error('scores', f"{error.message}") for error in errors]
            except JSONDecodeError:
                self.add_error('scores', "Invalid JSON")

        return self.cleaned_data
