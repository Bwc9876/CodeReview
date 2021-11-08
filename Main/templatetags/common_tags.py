"""
    This file defines common tags to use in templates
"""

from django import template
from django.contrib import messages
from django.template.defaultfilters import safe

register = template.Library()


@register.filter(name="make_spaces")
def make_spaces(in_string):
    """
        This filter takes a string an replaces all dashes and underscores with spaces

        :param in_string: The string to change
        :type in_string: str
        :returns: A string with no dashes or underscores
        :rtype: str
    """

    return in_string.replace("_", " ").replace("-", " ")


link_types = {
    'delete': 'link-danger',
    'abandon': 'link-danger',
    'cancel': 'link-danger',
}


@register.filter(name="link_class")
def get_link_class(action_name):
    """
        This filter gets what link class to use based off the action that it performs

        :param action_name: The name of the action
        :type action_name: str
        :returns: The link class that conveys what the action does
        :rtype: str
    """

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
    """
        This filter gets an alert class for the specified message type


        :param message_level: The level of the message
        :type message_level: int
        :returns: The corresponding alert class to use
        :rtype: str
    """

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
    """
        This filter gets an alert icon for the specified message type


        :param message_level: The level of the message
        :type message_level: int
        :returns: The corresponding alert icon to use
        :rtype: str
    """

    return f'bi bi-{icon_classes.get(message_level, "info-circle")}'


@register.simple_tag(name="external_link")
def external_link(href: str, display_text: str, classes: str = "") -> str:
    """
        This tag will render an <a> element that will open in a new tab and be marked as external

        :param href: The href of the link
        :type href: str
        :param display_text: The test to display in the <a> element
        :type display_text: str
        :param classes: Classes to add to the <a> element
        :type classes: str
        :returns: An <a> element in html that when clicked will open in a new tab
        :rtype: str
    """
    return safe(f'<a href="{href}" class="{classes}" target="_blank" rel="noopener">{display_text}</a>')
