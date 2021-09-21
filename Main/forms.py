from django.forms import Form, Field, TextInput
from django.forms.fields import CharField

from . import models


# class GradeWidget(TextInput):
#     template_name = "widgets/rubric_grade.html"
#     rubric = None
#
#     def get_context(self, name, value, attrs):
#         context = super().get_context(name, value, attrs)
#         context['widget']['rubric'] = self.rubric
#         return context
#
#
# class GradeField(Field):
#     widget = GradeWidget()
#
#
# class CompleteReviewForm(Form):
#
#     score = GradeField(required=True, label="Score")
#     additional_comments = CharField(required=True, label="Additional Comments")
#
#     def set_rubric(self, rubric):
#         self.score.widget.rubric = rubric

