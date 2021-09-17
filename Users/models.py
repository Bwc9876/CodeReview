from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser


class User (AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4)
    is_reviewer = models.BooleanField(default=False)

    def __str__(self):
        if self.first_name is None or self.last_name is None:
            return self.username
        else:
            return f'{self.first_name} {self.last_name}'
