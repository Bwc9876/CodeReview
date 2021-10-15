from django import template

register = template.Library()


@register.filter(name="make_spaces")
def make_spaces(in_string):
    return in_string.replace("_", " ").replace("-", " ")


link_types = {
    'delete': 'link-danger',
    'abandon': 'link-danger',
    'cancel': 'link-danger',
}


@register.filter(name="link_class")
def get_link_class(action_name):
    return link_types.get(action_name, "link-primary")
