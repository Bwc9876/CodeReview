"""
    This file defines additional context data that will be passed to templates
"""

from django.conf import settings
from django.http import HttpRequest

from Users.models import User


def base_context(request: HttpRequest) -> dict[str, object]:
    """
        This context processor gives some basic info to templates.
        'debug' tells the template if we're debugging right now.
        'base_template' signifies which template to use as a base depending on if the user is an instructor.

        :param request: The web request we've received
        :return: additional context to pass to the template
        :rtype: dict
    """

    user: User = request.user
    return {
        'debug': settings.DEBUG,
        'base_template': "admin_base.html" if user.is_superuser else "base.html"
    }
