from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4)
    is_reviewer = models.BooleanField(default=False)

    def __str__(self):
        if self.first_name == "" or self.last_name == "":
            return self.username
        else:
            return f'{self.first_name} {self.last_name}'
