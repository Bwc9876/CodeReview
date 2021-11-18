"""
    This file defines custom tags to use for emails
"""

from django import template

register = template.Library()


@register.inclusion_tag('emails/hr.html')
def separator() -> dict:
    """
        This tag creates a horizontal separator, usually you can do this with <hr>, however most email clients
        don't support it, so we need to make a work-around.
    """

    return {}


@register.inclusion_tag("emails/p_attrs.txt")
def p_attrs() -> dict:
    """
        This tag add common attributes to a <p> element that makes it look better on email clients
    """

    return {}
