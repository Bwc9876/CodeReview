
from django.conf import settings
from django.forms import ModelForm
from .models import User


class FinishUserForm(ModelForm):

    class Meta:
        model = User
        fields = ['student_id']

    def save(self, commit=True):
        new_user: User = super(FinishUserForm, self).save(commit=commit)
        new_user.email = f'{new_user.first_name[:3].lower()}{new_user.last_name[:3].lower()}{new_user.student_id[-3:]}@{settings.EMAIL_DOMAIN}'
        new_user.save()
        return new_user

