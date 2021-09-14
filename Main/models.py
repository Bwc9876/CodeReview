from uuid import uuid4

from django.db import models

from Users.models import User


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)

    class Meta:
        abstract = True


class Review(BaseModel):
    created = models.DateField(auto_now_add=True)
    from_user = models.ForeignKey(User, related_name="fromUser", on_delete=models.CASCADE)
    assigned_user = models.ForeignKey(User, related_name="assignedUser", on_delete=models.CASCADE,
                                      limit_choices_to={'reviewer': True}, null=True, blank=True)

    def __str__(self):
        if self.assigned_user is None:
            return f'Code Review Requested By {str(self.from_user)}'
        else:
            return f'Code Review Requested By {str(self.from_user)}, Assigned To {str(self.assigned_user)}'
