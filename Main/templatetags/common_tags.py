from django import template
from django.contrib import messages

import Users.models

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


level_classes = {
    messages.SUCCESS: "success",
    messages.ERROR: "danger",
    messages.DEBUG: "info",
    messages.INFO: "info",
    messages.WARNING: "warning",
}


@register.filter(name="alert_class")
def get_alert_class(message_level):
    return f'alert-{level_classes.get(message_level, "info")}'


icon_classes = {
    messages.SUCCESS: "check-circle",
    messages.ERROR: "exclamation-circle",
    messages.DEBUG: "info-circle",
    messages.INFO: "info-circle",
    messages.WARNING: "exclamation-triangle",
}


@register.filter(name="icon_class")
def get_icon_class(message_level):
    return f'bi bi-{icon_classes.get(message_level, "info-circle")}'


@register.filter()
def determine_base(user: Users.models.User):
    if user.is_superuser:
        return "admin_base.html"
    else:
        return "base.html"
