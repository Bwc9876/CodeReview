"""
    This file defines the forms used in the Users app
"""

from django.conf import settings
from django.forms import ModelForm, TextInput, CharField, ValidationError

from .models import User


class PartialInput(TextInput):
    """
        This widget defines a field that utilizes bootstrap's form groups to auto-fill parts of it.

        :cvar template_name: The template this widget renders to
    """

    template_name = "widgets/partial-input.html"

    def __init__(self, *args, **kwargs):
        """
            This function is run to instantiate the widget
        """

        self.prefixes = kwargs.get('prefixes', ())
        self.suffixes = kwargs.get('suffixes', ())
        super(PartialInput, self).__init__(*args, **kwargs)

    def format_value(self, value: str) -> str:
        """
            This function defines how the widget's value will be rendered to a string

            :param value: The value of the widget
            :type value: str
        """

        if value is not None and value != "":
            value = super(PartialInput, self).format_value(value)
            if len(self.prefixes) > 0:
                value = value[len(''.join(self.prefixes)):]
            if len(self.suffixes) > 0:
                value = value[:len(''.join(self.suffixes)) * -1]
        return value

    def get_context(self, name, value, attrs) -> dict:
        """
            This function defines additional context to pass to the widget's template

            :param name: The name of the widget
            :type name: str
            :param value: The value of the widget
            :type value: str
            :param attrs: The attributes to render in the template
            :type attrs: dict
            :returns: context to pass to the template
            :rtype: dict
        """

        context = super(PartialInput, self).get_context(name, value, attrs)
        context['widget']['prefixes'] = self.prefixes
        context['widget']['suffixes'] = self.suffixes
        return context


class PartialField(CharField):
    """
        This field utilizes bootstrap's form groups to auto-fill parts of it.
    """

    widget = PartialInput()

    is_admin = False

    def clean(self, value):
        """
            This function is run to convert the value to a string
            It adds the prefixes and suffixes to the value

            :param value: The value of the field
            :type value: str
            :returns: The value formatted to an email
            :rtype: str
        """

        if not self.is_admin:
            value = super(PartialField, self).clean(value)
            if len(value) < 3 or len(value) > 3:
                raise ValidationError("Please enter 3 digits")
            try:
                int(value)
            except ValueError:
                raise ValidationError("Must be a number")
        return f'{"".join(self.widget.prefixes)}{value}{"".join(self.widget.suffixes)}'


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
        fields = ['email']
        help_texts = {
            'email': "The email you'd like notifications to be sent to (should be a BCTC email)"
        }
        labels = {
            'email': "Email"
        }
        widgets = {
            'email': PartialInput()
        }
        field_classes = {
            'email': PartialField
        }

    def __init__(self, *args, **kwargs):
        """
            This function is used to instantiate a new form
        """

        super(FinishUserForm, self).__init__(*args, **kwargs)
        if self.instance.is_superuser:
            self.fields['email'].is_admin = True
            self.fields['email'].widget.suffixes = (f'@{settings.EMAIL_ADMIN_DOMAIN}',)
        else:
            self.fields['email'].widget.prefixes = (self.instance.first_name[:3].lower(), self.instance.last_name[:3].lower())
            self.fields['email'].widget.suffixes = (f'@{settings.EMAIL_DOMAIN}',)
            self.fields['email'].help_text = "Enter the last 3 digits of your student id"
