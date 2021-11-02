"""
    This file defines models that will converted to tables in the database for the Users app
"""

from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
        This model represents a User in the database

        :cvar id: A Unique Identifier for the user
        :cvar session: The session the student is in (AM or PM)
        :cvar is_reviewer: Whether the student can review code
    """

    class Session(models.TextChoices):
        """
            This internal class is used to store the types of sessions there are
        """

        AM = 'AM', "AM Session"
        PM = 'PM', "PM Session"

    id = models.UUIDField(primary_key=True, default=uuid4)
    session = models.CharField(choices=Session.choices, default=Session.AM, max_length=2)
    is_reviewer = models.BooleanField(default=False)

    @staticmethod
    def session_from_str(session_code: str) -> str:
        """
            This function takes a session code (AM or PM) and returns the label for it ("AM Session" or "PM Session")

            :param session_code: The key for the session in the Session enum
            :type session_code: str
            :returns: The label for the session
            :rtype: str
        """

        return User.Session.labels[User.Session.values.index(session_code)]

    def __str__(self) -> str:
        """
            This function define how this object will be casted to string.
            If the user has a first and last name, we use those, otherwise, we just use the username

            :returns: A string representation of this object
            :rtype: str
        """

        if self.first_name == "" or self.last_name == "":
            return self.username
        else:
            return f'{self.first_name} {self.last_name}'
