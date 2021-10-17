from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Session(models.TextChoices):
        AM = 'AM', "AM Session"
        PM = 'PM', "PM Session"

    id = models.UUIDField(primary_key=True, default=uuid4)
    session = models.CharField(choices=Session.choices, default=Session.AM, max_length=2)
    is_reviewer = models.BooleanField(default=False)

    @staticmethod
    def session_from_str(session_code):
        return User.Session.labels[User.Session.values.index(session_code)]

    def __str__(self):
        if self.first_name == "" or self.last_name == "":
            return self.username
        else:
            return f'{self.first_name} {self.last_name}'
