"""
    This file defines the backend code that runs when the user goes to a page
"""

from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.views.generic import TemplateView, UpdateView
from django.db.models import QuerySet

from .models import User
from .forms import FinishUserForm
from Main.views import FormNameMixin, FormAlertMixin


class CompleteUserSetupView(LoginRequiredMixin, FormNameMixin, FormAlertMixin, UpdateView):
    """
        This view is run when the user wishes to edit their student id

        :cvar template_name: The template to render
        :cvar form_name: The name to display in the pageHeader block
        :cvar form_class: The class to use when rendering the form
        :cvar model: The model we're editing
        :cvar success_message: The message that's displayed when the edit is a success
        :cvar success_url: The url to redirect to after the form is saved
    """

    template_name = "form_base.html"
    form_name = "Complete User Setup"
    form_class = FinishUserForm
    model = User
    success_message = "User Setup Complete"
    success_url = reverse_lazy('home')

    def get_queryset(self):
        """
            This function defines what users a user can edit the student ids of
            We only want a user to be able to edit their own ids

            :returns: The users the user is allowed to edit
            :rtype: QuerySet
        """

        return User.objects.filter(id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        """
            This function is run when the user makes a GET request
            If the user isn't from ActiveDirectory (they're an admin) we don't need to worry about student ids
        """

        if request.user.has_usable_password():
            if settings.DEBUG:
                messages.add_message(request, messages.WARNING, "User isn't from IIS. Ignoring because DEBUG is True")
            else:
                return redirect('home')
        return super(CompleteUserSetupView, self).get(request, *args, **kwargs)


class LogoutDoneView(TemplateView):
    """
        This view is shown when the user has been logged out
    """

    template_name = "logout_complete.html"
