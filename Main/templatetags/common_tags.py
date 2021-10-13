from django import template

register = template.Library()


@register.filter(name="make_spaces")
def make_spaces(in_string):
    return in_string.replace("_", " ").replace("-", " ")
