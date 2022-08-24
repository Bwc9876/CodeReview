"""
    This file defines the backend code that runs when the user goes to a page
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import QuerySet
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, UpdateView

from Main.views import FormNameMixin, FormAlertMixin
from .forms import FinishUserForm
from .models import User


class UserLoginView(FormAlertMixin, LoginView):
    """
        This view is used by the user to log in

        :cvar template_name: The template to render
        :cvar success_message: The message to display when the user has logged in (don't display one)
    """

    template_name = "login.html"

    success_message = None

    def get_context_data(self, **kwargs) -> dict[str, object]:
        """
            This function defines additional context data to pass to the template
            It hides the back button and displays some help info

            :returns: Context data to pass to the template
            :rtype: dict
        """

        context = super(UserLoginView, self).get_context_data(**kwargs)
        context['hide_back'] = True
        context['non_field_help_text'] = "Use your Office 365 credentials to log in"
        return context


class LogoutDoneView(TemplateView):
    """
        This view is shown when the user has been logged out
    """

    template_name = "logout_complete.html"
