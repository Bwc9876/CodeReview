"""
    This file defines tags related to forms to use in templates
"""

from django import template
from django.forms import BoundField

register = template.Library()


@register.filter(name="setup_field")
def setup_field(field: BoundField, with_placeholder=True) -> BoundField:
    """
        This filter sets up a field with proper css classes

        :param field: The field to set up
        :type field: BoundField
        :param with_placeholder: Whether to have a placeholder in the input element
        :type with_placeholder: bool
        :returns: The field as html with the added classes
        :rtype: str
    """

    validation_class = ""

    if field.errors:
        validation_class = "is-invalid"
    else:
        if field.name in field.form.changed_data and field.form.non_field_errors is None:
            validation_class = "is-valid"

    attrs = {
        'class': f"form-control {validation_class}",
        'aria-describedby': f"{field.name}-feedback"
    }

    if with_placeholder:
        attrs['placeholder'] = field.label

    new_field = field.as_widget(attrs=attrs)

    if field.field.show_hidden_initial:
        return new_field + field.as_hidden(only_initial=True)
    return new_field
