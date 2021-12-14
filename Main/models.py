"""
    This file defines models that will be converted to tables in the database for the Main app
"""

from typing import Optional, Union
from uuid import uuid4, UUID

from django.db import models

from Users.models import User


def val_uuid(src: Union[str, UUID]) -> Optional[UUID]:
    """
        This function takes a UUID in either a string or UUID format and ensures its valid

        :param src: The UUID to validate
        :type src: str
        :returns: The UUID as a UUID object
        :rtype: UUID
    """

    try:
        return UUID(src) if type(src) == str else src
    except ValueError:
        return None


class BaseModel(models.Model):
    """
        This model is inherited by other models to provide common functionality

        :cvar id: The primary key of each object, uses a UUID
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        """
            This internal class specifies settings for the model

            :cvar abstract: This is a special attribute that tells django not to save this model to the database
        """

        abstract = True

    @classmethod
    def max_length(cls, field_name: str) -> int:
        """
            This method gets the max length of a given field.

            :param field_name: The name of the field to get the max length of
            :type field_name: str
            :returns: The max length of the field
            :rtype: int
        """

        return cls._meta.get_field(field_name).max_length


class Review(BaseModel):
    """
        This model represents Review in the database

        :cvar student: The student that requested the Review
        :cvar reviewer: The reviewer that has accepted the Review
        :cvar schoology_id: The assignment id that this review pertains to
        :cvar status: The status of the review
        :cvar rubric: The Rubric the review is using
        :cvar additional_comments: Any additional comments the Reviewer has about the Review
        :cvar date_created: The date the Review was created
        :cvar date_completed: The date the Review was completed
    """

    class Status(models.TextChoices):
        """
            This internal class defines the statuses a review can have

            :cvar OPEN: The Review is open for a Reviewer to accept
            :cvar ASSIGNED: The Review has been claimed by a Reviewer
            :cvar CLOSED: The Review has been graded and closed
        """

        OPEN = 'O', "Open"
        ASSIGNED = 'A', "Taken"
        CLOSED = 'C', "Completed"

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer", null=True)
    schoology_id = models.CharField(max_length=10, null=True,
                                    help_text="The ID of the schoology assignment that this review pertains to")
    status = models.CharField(choices=Status.choices, default=Status.OPEN, max_length=1)
    rubric = models.ForeignKey("Instructor.Rubric", related_name="source_rubric", on_delete=models.CASCADE,
                               help_text="The rubric the reviewer will use to grade your code")
    additional_comments = models.TextField(blank=True, null=True,
                                           help_text="Any additional comments you have on the code")
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)

    class Meta:
        """
            This internal class specifies settings for the model

            :cvar ordering: Defines how the object will be ordered when queried
        """

        ordering = ['-date_completed', '-date_created']

    def __str__(self):
        """
            This function defines how the model will be cast to a string

            :returns: The student the Review is from
            :rtype: str
        """

        return f"Review from {str(self.student)}"

    def score_fraction(self):
        """
            This function returns the score a student got as a fraction.
            It will only run if the Review is closed

            :returns: The score the student got
            :rtype: str
        """

        if self.status == Review.Status.CLOSED:
            my_score = self.scoredrow_set.all().aggregate(models.Sum('score'))
            max_score = self.scoredrow_set.all().aggregate(models.Sum('source_row__max_score'))
            return f'{my_score["score__sum"]}/{max_score["source_row__max_score__sum"]}'
        else:
            return None

    @staticmethod
    def get_status_from_string(status):
        """
            This function gets the label for a status based off it's key ("O" would become "Open")

            :param status: The key for the status
            :type status: str
            :returns: The label for the given status key
            :rtype: str
        """

        return Review.Status.labels[Review.Status.values.index(status)]
