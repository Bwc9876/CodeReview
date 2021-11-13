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

    def get_context_data(self, **kwargs) -> dict:
        """
            This function defines additional data to pass to the template
            It disables placeholders as they mess up input groups

            :returns: context data to pass to the template
            :rtype: dict
        """

        context = super(CompleteUserSetupView, self).get_context_data(**kwargs)
        context['render_no_floating'] = True
        context['hide_back'] = self.object.email is None or self.object.email == ""
        return context


class UserLoginView(FormAlertMixin, LoginView):
    """
        This view is used by the user to log in

        :cvar template_name: The template to render
        :cvar success_message: The message to display when the user has logged in (don't display one)
    """

    template_name = "login.html"

    success_message = None

    def get_context_data(self, **kwargs) -> dict:
        """
            This function defines additional context data to pass to the template
            It hides the back button and displays some help info

            :returns: Context data to pass to the template
            :rtype: dict
        """

        context = super(UserLoginView, self).get_context_data(**kwargs)
        context['hide_back'] = True
        context['non_field_help_text'] = "Use your Windows credentials to log in"
        return context

    def get_success_url(self) -> str:
        """
            This function defines the url to go to when the user has logged in
            If this is the user's first time logging in, ask them for their email

            :returns: The url to go to after logging in
            :rtype: str
        """

        if self.request.user.email is None or self.request.user.email == "":
            return reverse('user-setup', kwargs={'pk': self.request.user.id})
        else:
            return super(UserLoginView, self).get_success_url()


class LogoutDoneView(TemplateView):
    """
        This view is shown when the user has been logged out
    """

    template_name = "logout_complete.html"
