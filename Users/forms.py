"""
    This file defines the forms used in the Users app
"""


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
        fields = ['email']
        help_texts = {
            'email': "The email you'd like notifications to be sent to (should be a BCTC email)"
        }
