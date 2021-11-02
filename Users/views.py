"""
    This file defines the backend code that runs when the user goes to a page
"""

from django.views.generic import TemplateView


class LogoutDoneView(TemplateView):
    """
        This view is shown when the user has been logged out
    """

    template_name = "logout_complete.html"
