"""
    This file defines the forms used in the Users app
"""


from django.conf import settings
from django.forms import ModelForm
from .models import User


class FinishUserForm(ModelForm):
    """
        This form is used to finish setting up a user when syncing them from ActiveDirectory
    """

    class Meta:
        """
            This internal class defines options for the form

            :cvar model: The model we want the form to edit
            :cvar fields: The fields on the model we want to edit
        """

        model = User
        fields = ['student_id']

    def save(self, commit=True):
        """
            This code is run when the form is saved.
            It generates the student's email address from their first name, last name, and student id.

            :param commit: Whether to save changes made or not:
            :type commit: bool
            :returns: The edited user object
            :rtype: User
        """

        new_user: User = super(FinishUserForm, self).save(commit=commit)
        new_user.email = f'{new_user.first_name[:3].lower()}{new_user.last_name[:3].lower()}{new_user.student_id[-3:]}@{settings.EMAIL_DOMAIN}'
        new_user.save()
        return new_user

