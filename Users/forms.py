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
        :cvar help_texts: The help text to the show for fields
        :cvar labels: The label to show for fields
        :cvar widgets: The widgets to show for fields
        :cvar field_classes: The Field classes to use when rendering fields
        """

        model = User
        fields = ["receive_notifications", "gay_mode"]
