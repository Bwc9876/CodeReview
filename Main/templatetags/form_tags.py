"""
    This file defines tags related to forms to use in templates
"""

from django import template
from django.forms import BoundField
from django.forms.fields import CheckboxInput

register = template.Library()


@register.filter(name="is_checkbox")
def is_checkbox(field: BoundField):
    """
    This function is used to check if a given field is a checkbox
    @param field: The field to check
    @type field: Field
    @return: Whether it's a checkbox
    @rtype: bool
    """

    return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__


@register.filter()
def setup_checkbox(field: BoundField):
    return field.as_widget(attrs={"role": "switch", "class": "form-check-input"})


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

    attrs = {
        "class": f"form-control {validation_class}",
        "aria-describedby": f"{field.name}-feedback",
    }

    if with_placeholder:
        attrs["placeholder"] = field.label

    new_field = field.as_widget(attrs=attrs)

    return new_field
