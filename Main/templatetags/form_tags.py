from django import template
from django.forms import BoundField

register = template.Library()


@register.filter(name="setup_field")
def setup_field(field: BoundField, classes: str) -> BoundField:
    validation_class = ""

    if field.errors:
        validation_class = "is-invalid"
    else:
        if field.name in field.form.changed_data and field.form.non_field_errors is None:
            validation_class = "is-valid"

    attrs = {
        'class': f"{classes} {validation_class}",
        'placeholder': field.label,
        'aria-describedby': f"{field.name}-feedback"
    }

    new_field = field.as_widget(attrs=attrs)

    if field.field.show_hidden_initial:
        return new_field + field.as_hidden(only_initial=True)
    return new_field
