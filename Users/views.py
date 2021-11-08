"""
    This file defines the backend code that runs when the user goes to a page
"""

from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.views.generic import TemplateView, UpdateView

from .models import User
from .forms import FinishUserForm
from Main.views import FormNameMixin, FormAlertMixin


class CompleteUserSetupView(LoginRequiredMixin, FormNameMixin, FormAlertMixin, UpdateView):
    template_name = "form_base.html"
    form_name = "Complete User Setup"
    form_class = FinishUserForm
    model = User
    success_message = "User Setup Complete"
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get(self, request, *args, **kwargs):
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
