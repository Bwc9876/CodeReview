"""
    This file defines the back-end code that runs when a user requests a page for the Instructor app
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View, ListView, TemplateView, CreateView, UpdateView, DeleteView

from Main import models as main_models
from Main.views import IsSuperUserMixin, FormNameMixin, FormAlertMixin, SuccessDeleteMixin
from Users.ldap_auth import LDAPAuthentication
from Users.ldap_errors import LDAPAuthException
from Users.ldap_mock import LDAPMockAuthentication
from Users.models import User
from . import models, forms


class UserClearView(LoginRequiredMixin, IsSuperUserMixin, View):
    """
        This view is used to clean up any users that are not in the ActiveDirectory database.

        :cvar http_method_names: The HTTP methods that this view takes
    """

    http_method_names = ['post']

    def post(self, request):
        """
            This function is run when on a POST request.
            It clears out users that are not in the ActiveDirectory database.
        """

        self.request = request
        password = self.request.POST.get("userPassword", None)
        if password is None or password == "":
            messages.add_message(self.request, messages.ERROR, "Please provide a password")
            return redirect("user-list")
        else:
            try:
                backend = LDAPMockAuthentication \
                    if settings.AUTHENTICATION_BACKENDS[0] == "Users.ldap_mock.LDAPMockAuthentication" \
                    else LDAPAuthentication
                backend().delete_old_users(self.request.user.username, password)
                messages.add_message(self.request, messages.SUCCESS, "Users Cleared Successfully")
                return redirect("user-list")
            except LDAPAuthException as error:
                messages.add_message(self.request, messages.ERROR, error.args[0])
                return redirect("user-list")


class AdminHomeView(LoginRequiredMixin, IsSuperUserMixin, TemplateView):
    """
        This view shows the Instructor's homepage, where they can view ongoing and completed Reviews

        :cvar template_name: The template to render and return to the user
    """

    template_name = "admin_home.html"

    def get_context_data(self, **kwargs) -> dict:
        """
            This function defines additional context to pass to the template in `AdminHomeView.template_name`

            :returns: A dictionary that hold context to pass to the template
            :rtype: dict
        """

        context = super().get_context_data(**kwargs)
        active = main_models.Review.objects.exclude(status=main_models.Review.Status.CLOSED)
        completed = main_models.Review.objects.filter(status=main_models.Review.Status.CLOSED)
        context['am_active'] = active.filter(student__session=User.Session.AM)
        context['am_completed'] = completed.filter(student__session=User.Session.AM)
        context['pm_active'] = active.filter(student__session=User.Session.PM)
        context['pm_completed'] = completed.filter(student__session=User.Session.PM)
        return context


class UserListView(LoginRequiredMixin, IsSuperUserMixin, TemplateView):
    """
        This view shows a list of users that the instructor can set as reviewers

        :cvar template_name: The template to render and return to the user
        :cvar http_method_names: The HTTP methods to accept from the client
        :cvar _schema: We use this dictionary to validate JSON a client has sent us
    """

    template_name = "user_list.html"
    http_method_names = ['get', 'post']

    @staticmethod
    def get_queryset():
        """
            This defines what objects from the database to list.
            We don't want Instructors to be listed, so we exclude them

            :returns: A QuerySet with non-instructor user
            :rtype: QuerySet
        """

        return User.objects.filter(is_superuser=False)

    def post(self, *args, **kwargs):
        """
            This function defines back-end behaviour when the user uses the POST method.
            It updates sessions and reviewers based off user input.
        """
        reviewer_query = Q(id__in=self.request.POST.getlist('reviewers'))
        self.get_queryset().filter(reviewer_query).update(is_reviewer=True)
        self.get_queryset().filter(~reviewer_query).update(is_reviewer=False)
        self.get_queryset().filter(id__in=self.request.POST.getlist("to_delete")).delete()
        messages.add_message(self.request, messages.SUCCESS, "Users Updated")
        return redirect("user-list")

    def get_context_data(self, **kwargs):
        """
            This function gives additional context to pass to the template

            :returns: A dictionary that has context for the template
            :rtype: dict
        """

        context = super(UserListView, self).get_context_data(**kwargs)
        context['AM'] = self.get_queryset().filter(session=User.Session.AM)
        context['PM'] = self.get_queryset().filter(session=User.Session.PM)
        return context


# Rubrics


class RubricListView(LoginRequiredMixin, IsSuperUserMixin, ListView):
    """
        This View lists the Rubric in the database

        :cvar template_name: The template to render and pass to the user
        :cvar model: The model django will list and show to the user
        :cvar context_object_name: The name of the list that is passed to the template as context
    """

    template_name = 'rubrics/rubric_list.html'
    model = models.Rubric
    context_object_name = 'rubrics'


class RubricCreateView(LoginRequiredMixin, IsSuperUserMixin, FormNameMixin, FormAlertMixin, CreateView):
    """
        This view is used to create Rubrics

        :cvar form_class: The form to render in the template
        :cvar success_url: The url to go to if the creation was successful
        :cvar template_name: The template to render and return to the user
        :cvar form_name: The name of the form to display as the Page Header
        :cvar success_message: The message that will appear as an alert when the creation is done
    """

    form_class = forms.RubricForm
    success_url = reverse_lazy('rubric-list')
    template_name = 'form_base.html'
    form_name = "Create Rubric"
    success_message = "New Rubric Saved"


class RubricEditView(LoginRequiredMixin, IsSuperUserMixin, FormNameMixin, FormAlertMixin, UpdateView):
    """
        This view is used to edit Rubrics

        :cvar form_class: The form to render in the template
        :cvar success_url: The url to go to if the edit was successful
        :cvar template_name: The template to render and return to the user
        :cvar form_name: The name of the form to display as the Page Header
        :cvar success_message: The message that will appear as an alert when the editing is done
    """

    form_class = forms.RubricForm
    form_name = "Edit Rubric"
    model = models.Rubric
    success_url = reverse_lazy('rubric-list')
    template_name = 'form_base.html'
    success_message = "Rubric Updated"

    def form_valid(self, form):
        """
            This function is run when the form is valid.
            This handles when an Instructor changes a Rubric that is used in a Review that has been graded.

            :param form: The form that is valid
            :type form: Form
        """

        edited_object = form.save()
        row_count = edited_object.rubricrow_set.count()
        for review in main_models.Review.objects.filter(rubric=edited_object, status=main_models.Review.Status.CLOSED):
            if review.scoredrow_set.count() != row_count:
                for row in edited_object.rubricrow_set.all():
                    try:
                        review.scoredrow_set.get(source_row__index=row.index)
                    except models.ScoredRow.DoesNotExist:
                        scored = review.scoredrow_set.create(score=-1, source_row=row)
                        scored.save()
                review.scoredrow_set.filter(source_row__index__gte=row_count).delete()

        return super(RubricEditView, self).form_valid(form)


class RubricDupeView(LoginRequiredMixin, IsSuperUserMixin, View):
    """
        This view duplicates a given rubric

        :cvar http_method_names: The names of the accepted http methods to use
    """

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
            This method is run when the view receives a POST request

            It duplicates the provided rubric
        """

        try:
            target_rubric: models.Rubric = models.Rubric.objects.select_related().get(id=kwargs.get('pk'))
            self.request = request
            if len(target_rubric.name) + 10 > 50:
                new_name = "New Rubric"
                messages.add_message(request, messages.WARNING,
                                     "The length of the name is too long; the rubric has been named \"New Rubric\"")
            else:
                new_name = f"Copy of {target_rubric.name}"
            new_rubric = models.Rubric.objects.create(name=new_name, max_score=target_rubric.max_score)
            new_rubric.save()
            for row in target_rubric.rubricrow_set.all():
                new_row = models.RubricRow.objects.create(name=row.name, description=row.description,
                                                          max_score=row.max_score, parent_rubric_id=new_rubric.id,
                                                          index=row.index)
                new_row.save()
                for cell in row.rubriccell_set.all():
                    new_cell = models.RubricCell.objects.create(score=cell.score, description=cell.description,
                                                                parent_row_id=new_row.id, index=cell.index)
                    new_cell.save()
            messages.add_message(request, messages.SUCCESS, "Rubric Duplicated")
            return redirect('rubric-list')
        except models.Rubric.DoesNotExist:
            raise Http404("Rubric Not Found")


class RubricDeleteView(LoginRequiredMixin, IsSuperUserMixin, SuccessDeleteMixin, DeleteView):
    """
        This view is used to confirm with the user that they want to delete a Rubric

        :cvar template_name: The template to render and return to the user
        :cvar model: The model that we want to delete
        :cvar success_url: The url to redirect to when the deletion is done
        :cvar success_message: The message to show when the deletion is complete
    """

    template_name = 'rubrics/rubric_delete.html'
    model = models.Rubric
    success_url = reverse_lazy('rubric-list')
    success_message = "Rubric Deleted"

    def get_context_data(self, **kwargs):
        """
            This function defines additional data that is passed to the template

            :return: A dictionary with the context to pass
            :rtype: dict
        """

        context = super(RubricDeleteView, self).get_context_data(**kwargs)
        context['objectString'] = self.object.name
        return context
