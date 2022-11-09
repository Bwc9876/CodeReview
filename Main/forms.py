"""
    This file defines the forms used in the Main app
"""

from json import JSONDecoder, JSONDecodeError
from re import fullmatch
from typing import List

from django.db.models import Q
from django.forms import ModelForm, TextInput, Textarea, ValidationError
from django.forms.fields import CharField
from jsonschema.validators import Draft202012Validator

from Instructor.models import RubricRow, ScoredRow
from . import models


class GradeReviewWidget(TextInput):
    """
    This widget displays a table the user can click to grade a review

    :cvar template_name: The template to use to render this widget
    :cvar input_type: The type of the <input> element
    :cvar rubric: The rubric that the Review is using
    """

    template_name = "widgets/rubric_grade.html"
    input_type = "hidden"
    rubric = None

    class Media:
        """
        This internal class specifies additional resources the widget needs

        :cvar css: The CSS to include with the widget
        :cvar js: The JavaScript to use with the widget
        """

        css = {"all": ("css/rubrics/rubric_table.css",)}
        js = ("js/rubrics/rubric-grade-widget.js",)

    def get_context(self, name, value, attrs) -> dict[str, object]:
        """
        This function defines context to pass when rendering this widget

        :return: The context for the template
        :rtype: dict
        """

        context = super().get_context(name, value, attrs)
        context["widget"]["rubric"] = self.rubric
        return context


class ReviewForm(ModelForm):
    """
    This form is used when requesting/editing a review
    """

    SCHOOLOGY_ID_ERROR_MESSAGE = (
        "Schoology ID should be in format: XX.XX.XX where X'es are numbers"
    )

    def __init__(self, *args, **kwargs):
        """
        This function is run to initialize an instance of the form
        It sets self.user to the user kwarg
        """

        if "user" in kwargs.keys():
            self.user = kwargs.pop("user")
        else:
            self.user = None
        super().__init__(*args, **kwargs)

    class Meta:
        """
        This internal class specifies options for this form

        :cvar; The model this form edits
        :cvar fields: The fields to include on the form
        """

        model = models.Review
        fields = ["schoology_id", "rubric"]

    def clean(self) -> None:
        """
        This function is run to validate form data.
        It ensures that a student can only  have two requested reviews at once.
        It also validates the schoology id.
        """

        if (
            self.user is not None
            and models.Review.objects.filter(student=self.user)
            .filter(
                Q(status=models.Review.Status.OPEN)
                | Q(status=models.Review.Status.ASSIGNED)
            )
            .count()
            >= 2
        ):
            raise ValidationError("You can only have 2 requested reviews at once.")

        super(ReviewForm, self).clean()
        schoology_id = self.cleaned_data.get("schoology_id", None)
        if (schoology_id is not None) and not fullmatch(
            r"\d{2}\.\d{2}\.\d{2}", schoology_id
        ):
            self.add_error("schoology_id", self.SCHOOLOGY_ID_ERROR_MESSAGE)

    def save(self, commit=True) -> models.Review:
        """
        This function is run to save the new Review
        It sets the review's student to the user that submitted the form

        :param commit: Whether to actually save the new Review
        :type commit: bool
        :returns: The new review
        :rtype: models.Review
        """

        new_review: models.Review = super(ReviewForm, self).save(commit=False)
        if self.user is not None:
            new_review.student = self.user
        if commit:
            new_review.save()
        return new_review


class GradeReviewForm(ModelForm):
    """
    This form is used to grade Reviews

    :cvar scores: The scores as a JSON string to be encoded into ScoredRow objects
    :cvar _validation_schema: The schema used to ensure JSON is valid
    :cvar field_order: The order in which fields will appear in the form
    :ivar _json_validator: The validator used to ensure JSON is formatted correctly
    """

    scores = CharField(
        max_length=200,
        widget=GradeReviewWidget(),
        help_text="Please fill out each row in the rubric.",
    )

    _validation_schema = {"type": "array", "items": {"type": "number", "minimum": 0}}

    def __init__(self, *args, **kwargs):
        """
        This function is run to initialize a new instance of the form
        It loads the instance passed as a kwarg

        :raises: ValueError: If a Review object is not passed in kwargs
        """

        instance: models.Review = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)
        if instance:
            self.rubric = instance.rubric
            self.fields["scores"].widget.rubric = self.rubric
        else:
            raise ValueError("An instance must be provided to GradeReviewForm!")
        target_item_length = self.rubric.rubricrow_set.count()
        self._validation_schema["maxItems"] = target_item_length
        self._validation_schema["minItems"] = target_item_length
        self._json_validator = Draft202012Validator(self._validation_schema)

    class Meta:
        """
        This internal class defines settings for the Form

        :cvar model: The model the form is working with
        :cvar fields: The fields to use in the form
        :cvar widgets: The widgets each field will use
        """

        model = models.Review
        fields = ["additional_comments"]
        widgets = {"additional_comments": Textarea(attrs={"style": "height: 150px;"})}

    def save(self, commit=True) -> models.Review:
        """
        This function runs when the Form is saving
        It reads the scores from JSON and makes ScoredRow objects

        :param commit: Whether to save the changes to the database
        :type commit: bool
        :return: The newly graded Review
        :rtype: models.Review
        """

        new_review: models.Review = super(GradeReviewForm, self).save(commit=False)
        scores_array: List[str] = JSONDecoder().decode(self.cleaned_data.get("scores"))
        for i in range(len(scores_array)):
            score = float(scores_array[i])
            row = RubricRow.objects.get(parent_rubric=new_review.rubric, index=i)
            scored_row = ScoredRow.objects.create(
                source_row=row, parent_review=new_review, score=score
            )
            scored_row.save()
        new_review.status = models.Review.Status.CLOSED
        if commit:
            new_review.save()
        return new_review

    field_order = ["scores", "additional_comments"]

    def clean(self) -> None:
        """
        This function is used to validate input data.
        It ensures the JSON submitted for scores is valid and readable.

        :return: The cleaned input data
        :rtype: dict
        """

        cleaned_data: dict = super(GradeReviewForm, self).clean()
        scores_json: str = cleaned_data.get("scores")

        if scores_json:
            try:
                parsed = JSONDecoder().decode(scores_json)
                errors = sorted(self._json_validator.iter_errors(parsed), key=str)
                [self.add_error("scores", f"{error.message}") for error in errors]
                if len(errors) == 0:
                    for index, row in enumerate(self.rubric.rubricrow_set.all()):
                        if (
                            row.rubriccell_set.filter(score=parsed[index]).exists()
                            is False
                        ):
                            self.add_error(
                                "scores",
                                f"Invalid score: {parsed[index]} for row {index + 1}",
                            )
            except JSONDecodeError:
                self.add_error("scores", "Invalid JSON")
