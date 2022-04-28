"""
    This file defines backend code that runs when a user visits a page
"""

from datetime import datetime
from typing import Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core import mail
from django.db.models import Q, QuerySet
from django.forms import Form
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, DetailView, ListView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin, DeletionMixin

from Users.models import User
from . import models, forms


# Email Utility Functions


def send_email(subject_template: str, text_template: str, template_name: str, review: models.Review,
               query_set: QuerySet):
    """
        This function sends an email to a group of users

        :param subject_template: Defines what the subject of the email will be
        :type subject_template: str
        :param text_template: Defines what the text content will be
        :type text_template: str
        :param template_name: Defines what template to use for the html content of the email
        :type template_name: str
        :param review: The Review this email pertains to
        :type review: models.Review
        :param query_set: The QuerySet of users to send the email to
        :type query_set: QuerySet
    """

    for user in list(query_set.filter(receive_notifications=True)):
        html_content = render_to_string(template_name, {'target_user': user, 'review': review})
        text_content = text_template.format(target_user=str(user), student=str(review.student),
                                            reviewer=str(review.reviewer))
        subject = subject_template.format(target_user=str(user), student=str(review.student),
                                          reviewer=str(review.reviewer))
        message = mail.EmailMultiAlternatives(subject=f'{review.student.session} | {subject}', body=text_content)
        message.attach_alternative(html_content, "text/html")
        message.to = [user.email]
        message.send()


# Mixins
"""
    These mixins provide common functionality to Views
"""


class IsSuperUserMixin(UserPassesTestMixin):
    """
        This Mixin ensures the user is an admin (instructor)
    """

    request = None

    def test_func(self) -> bool:
        """
            This is the function run to test the user

            :returns: The user's superuser status
            :rtype: bool
        """

        return self.request.user.is_superuser


class IsReviewerMixin(UserPassesTestMixin):
    """
        This Mixin ensures the user is a reviewer
    """

    request = None

    def test_func(self) -> bool:
        """
            This is the function run to test the user

            :returns: The user's reviewer status
            :rtype: bool
        """

        return self.request.user.is_reviewer


class FormNameMixin(ContextMixin):
    """
        This Mixin lets Views set a "Form name" to be used in form_base.html

        :cvar form_name: The name of the form to display in the pageHeader block
    """

    form_name = "Form"

    def get_context_data(self, **kwargs) -> dict[str, object]:
        """
            This function is run to get additional context data to pass to the template

            :returns: Additional context to pass to the template
            :rtype: dict
        """

        context = super(FormNameMixin, self).get_context_data(**kwargs)
        context['formName'] = self.form_name
        return context


class FormAlertMixin(FormMixin):
    """
        This Mixin lets Forms display success and error messages

        :cvar success_message: The message to show when the form is valid
        :cvar failure_message: The message to show in the event of an error
    """

    request = None

    success_message: str = "Complete"
    failure_message: str = "The information you provided was incorrect, please correct the errors described below"

    def form_valid(self, form) -> HttpResponse:
        """
            This function is run when the form is valid.
            It adds the success message to the messages framework

            :param form: The form that is valid
        """

        if self.success_message is not None:
            messages.add_message(self.request, messages.SUCCESS, self.success_message)
        return super(FormAlertMixin, self).form_valid(form)

    def form_invalid(self, form: Form) -> HttpResponse:
        """
            This function is run when the form is invalid.
            It adds the failure message to the messages framework

            :param form: The form that is invalid
        """

        if len(form.non_field_errors()) > 0:
            for error in form.non_field_errors():
                messages.add_message(self.request, messages.ERROR, error)
        else:
            messages.add_message(self.request, messages.ERROR, self.failure_message)
        return super(FormAlertMixin, self).form_invalid(form)


class SuccessDeleteMixin(DeletionMixin):
    """
        This Mixin lets Views show a message after a deletion is complete.

        :cvar success_message: The message to be displayed when something is deleted successfully.
    """

    success_message: str = "Deleted"
    request = None

    def form_valid(self, form) -> HttpResponse:
        """
            This function is run when the deletion has been confirmed by the user.
            It adds the success message to the messages framework.
        """

        messages.add_message(self.request, messages.SUCCESS, self.success_message)
        return super(SuccessDeleteMixin, self).delete(self.request)


# Home


class HomeView(LoginRequiredMixin, TemplateView):
    """
        This view is shown when the User goes to the root of the site.

        :cvar template_name: The template to render
    """

    template_name = "home.html"

    def get(self, *args, **kwargs) -> HttpResponse:
        """
            This function is run when the user makes a GET request.
            It redirects the user to the instructor homepage if they're an instructor.
        """

        if self.request.user.email is None or self.request.user.email == "":
            return redirect('user-setup', pk=self.request.user.id)
        else:
            if self.request.user.is_superuser:
                return redirect('instructor-home')
            else:
                return super(HomeView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, object]:
        """
            This function gives additional context data to the template.
            It gives a list of Reviews related to the user.

            :returns: Additional context data for the template
            :rtype: dict
        """

        context = super(HomeView, self).get_context_data(**kwargs)
        user: User = self.request.user
        context['active'] = models.Review.objects.filter(student=user).exclude(status=models.Review.Status.CLOSED)
        context['completed'] = models.Review.objects.filter((Q(student=user) | Q(reviewer=user))
                                                            & Q(status=models.Review.Status.CLOSED))
        if user.is_reviewer:
            rubrics = models.Review.objects.exclude(status=models.Review.Status.CLOSED).filter(
                Q(status=models.Review.Status.OPEN, ) | Q(status=models.Review.Status.ASSIGNED, reviewer=user)
            )
            context['open'] = rubrics.filter(status=models.Review.Status.OPEN, student__session=user.session).exclude(
                student=user)
            context['assigned'] = rubrics.filter(status=models.Review.Status.ASSIGNED)

        return context


# Reviews


class ReviewCreateView(LoginRequiredMixin, FormNameMixin, FormAlertMixin, CreateView):
    """
        This view is used to create (request) a code review

        :cvar template_name: The name of the template to render
        :cvar success_url: The URL to go to if the creation was successful
        :cvar model: The model to create an object for
        :cvar form_class: The class of the Form to use
        :cvar form_name: The name to put in the pageHeader block
        :cvar success_message: The message to display when the creation is successful
    """

    template_name = 'form_base.html'
    success_url = reverse_lazy('home')
    model = models.Review
    form_class = forms.ReviewForm
    form_name = "Create a Review"
    success_message = "New Review Saved"

    def get_context_data(self, **kwargs) -> dict[str, object]:
        """
            This function defines additional context data to pass to the template
        """

        context = super(ReviewCreateView, self).get_context_data(**kwargs)
        context['render_no_floating'] = True
        return context

    def get_form_kwargs(self) -> dict[str, object]:
        """
            This function defines additional kwargs to pass to the form's constructor
            We give the user object so the Form can save the Review correctly

            :returns: Additional kwargs to pass to the Form's constructor
            :rtype: dict
        """

        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form) -> HttpResponse:
        """
            This function is run when the form has been submitted and is valid
            It sends an email to all Reviewers telling them about the new Review
        """

        response = super(ReviewCreateView, self).form_valid(form)
        send_email("Review created by {student}",
                   "Hello {target_user}, a new review has been created by {student}",
                   "emails/review_created.html",
                   self.object,
                   User.objects.filter(is_reviewer=True, session=self.request.user.session).exclude(
                       id=self.request.user.id))
        return response


class ReviewEditView(LoginRequiredMixin, FormNameMixin, FormAlertMixin, UpdateView):
    """
        This view is used to edit a code review

        :cvar template_name: The name of the template to render
        :cvar success_url: The URL to go to if the edit was successful
        :cvar model: The model to edit an object for
        :cvar form_class: The class of the form to render
        :cvar form_name: The name to put in the pageHeader block
        :cvar success_message: The message to display when the edit is successful
    """

    template_name = 'form_base.html'
    success_url = reverse_lazy('home')
    model = models.Review
    form_class = forms.ReviewForm
    form_name = "Edit Review"
    success_message = "Review Updated"

    def get_queryset(self) -> QuerySet:
        """
            This function defines which Reviews a user can edit
            It only lets you edit a review in which you are the student, and it's not graded

            :return: A QuerySet defining which Reviews can be edited by this user
            :rtype: QuerySet
        """

        return models.Review.objects.filter(student=self.request.user).exclude(status=models.Review.Status.CLOSED)


class ReviewCancelView(LoginRequiredMixin, SuccessDeleteMixin, DeleteView):
    """
        This view is used to cancel a Review.
        This is used by the *student* when they want to cancel a Review before it's done

        :cvar template_name: The template to render
        :cvar success_url: The URL to redirect to once the Review has been cancelled
        :cvar model: The model that will be deleted
        :cvar success_message: The message to display when the Review has been cancelled
    """

    template_name = 'reviews/review_cancel.html'
    success_url = reverse_lazy('home')
    model = models.Review
    success_message = "Review Cancelled"

    def get_context_data(self, **kwargs) -> dict[str, object]:
        """
            This function provides additional context data to the template

            :returns: Additional context to pass to the template
            :rtype: dict
        """

        context = super(ReviewCancelView, self).get_context_data(**kwargs)
        context['objectString'] = f"review with schoology id: {self.object.schoology_id}"
        return context

    def get_queryset(self) -> QuerySet:
        """
            This function defines what Reviews the user can cancel
            It limits it to the Reviews where the user is the student and Reviews that aren't closed

            :returns: A QuerySet of Reviews the user can edit
            :rtype: QuerySet
        """

        return models.Review.objects.filter(student=self.request.user).exclude(status=models.Review.Status.CLOSED)


class ReviewDeleteView(LoginRequiredMixin, IsSuperUserMixin, SuccessDeleteMixin, DeleteView):
    """
        This view is used to delete a Review.
        This is used by the *instructor* when they want to delete a Review after it's graded.

        :cvar template_name: The template to render
        :cvar success_url: The URL to redirect to once the Review has been deleted
        :cvar model: The model that will be deleted
        :cvar success_message: The message to display when the Review has been deleted
    """

    template_name = 'reviews/review_delete.html'
    success_url = reverse_lazy('home')
    model = models.Review
    success_message = "Review Deleted"

    def get_context_data(self, **kwargs) -> dict[str, object]:
        """
            This function provides additional context data to the template

            :returns: Additional context to pass to the template
            :rtype: dict
        """

        context = super(ReviewDeleteView, self).get_context_data(**kwargs)
        context['objectString'] = f"review from {self.object.student}"
        return context


class ReviewClaimView(LoginRequiredMixin, IsReviewerMixin, View):
    """
        This view is used by a reviewer to claim a review
        It only accepts POST request because the claim link on the homepage is actually just a form

        :cvar http_method_names: The accepted HTTP methods that this view takes
    """

    http_method_names = ['post']

    def post(self, request, *args, **kwargs) -> HttpResponse:
        """
            This function defines what will happen on a POST request

            :param request: The request that invoked this method
        """

        if models.Review.objects.filter(reviewer=request.user, status=models.Review.Status.ASSIGNED).count() >= 2:
            messages.add_message(request, messages.ERROR, "You can only have 2 claimed reviews at once")
            return redirect('home')
        else:
            target_pk = kwargs.get('pk', '')
            try:
                target_object = models.Review.objects.get(id=models.val_uuid(target_pk),
                                                          status=models.Review.Status.OPEN,
                                                          student__session=self.request.user.session)
                target_object.status = models.Review.Status.ASSIGNED
                target_object.reviewer = request.user
                target_object.save()
                send_email("Review accepted by {reviewer}",
                           "Hello, {target_user}, a review by {student} has been accepted by {reviewer}.",
                           "emails/review_accepted.html",
                           target_object,
                           User.objects.filter(is_superuser=True))
                messages.add_message(request, messages.SUCCESS, "Review Claimed")
                return redirect('home')
            except models.Review.DoesNotExist:
                raise Http404()


class ReviewerAction(LoginRequiredMixin, IsReviewerMixin, View):
    """
        This is an abstract class that provides functionality for performing an action on a review
    """

    def get_target_review(self, target_id: str) -> models.Review:
        """
            This function tries to get the Review specified by the ID in the url

            :param target_id: The id of the Review
            :type target_id: str
            :returns: A Review (if one is found)
            :rtype: Review
            :raises Http404: If no review was found
        """

        try:
            return models.Review.objects.get(id=models.val_uuid(target_id),
                                             status=models.Review.Status.ASSIGNED, reviewer=self.request.user)
        except models.Review.DoesNotExist:
            raise Http404


class ReviewAbandonView(ReviewerAction):
    """
        This view is used by a reviewer if they want to abandon a review.

        :cvar http_method_names: The accepted HTTP methods that this view takes
    """

    http_method_names = ['get', 'post']

    def post(self, *args, **kwargs) -> HttpResponseRedirect:
        """
            This function is run when a POST request is received

            It abandons the Review (makes it open for another Reviewer to take)
        """

        target_object = self.get_target_review(kwargs.get('pk', ""))
        target_object.status = models.Review.Status.OPEN
        target_object.reviewer = None
        target_object.save()
        messages.add_message(self.request, messages.SUCCESS, "Review Abandoned")
        return redirect('home')

    def get(self, *args, **kwargs) -> HttpResponse:
        """
            This function is run when a GET request is received

            It confirms that the user wants to abandon the Review
        """

        target_object = self.get_target_review(kwargs.get('pk', ""))
        return render(self.request, 'reviews/review_abandon.html', {'review': target_object,
                                                                    'objectString':
                                                                        f"review with {target_object.student}"})


class ReviewGradeView(LoginRequiredMixin, IsReviewerMixin, FormNameMixin, FormAlertMixin, UpdateView):
    """
        This view is used by a Reviewer when they want to grade a review.

        :cvar template_name: The template to render
        :cvar success_url: The URL to redirect to once the Review has been graded
        :cvar model: The model that we're editing
        :cvar success_message: The message to display when the Review has been graded
        :cvar form_name: The name to display in the pageHeader block
        :cvar form_class: The class of the form to render
    """

    template_name = 'form_base.html'
    success_url = reverse_lazy('home')
    model = models.Review
    form_class = forms.GradeReviewForm
    form_name = "Grade Review"
    success_message = "Review Graded"

    def get_queryset(self) -> QuerySet:
        """
            This function defines what Reviews can be graded
            It restricts it to Reviews that are assigned and reviews where the user is the reviewer

            :returns: A QuerySet defining which Reviews can be graded
            :rtype: QuerySet
        """

        return models.Review.objects.filter(reviewer=self.request.user, status=models.Review.Status.ASSIGNED)

    def form_valid(self, form) -> HttpResponse:
        """
            This function is run if the form is valid
            It saves the date and time the Review was graded and sends an email to the instructor

            :param form: The form that is valid
        """

        self.object.date_completed = datetime.now()
        self.object.save()
        response = super().form_valid(form)
        send_email("Review completed by {reviewer}",
                   "Hello, {target_user}, the review requested by {student} has been completed by {reviewer}.",
                   "emails/review_completed.html",
                   self.object,
                   User.objects.filter(is_superuser=True))
        self.object.reviewer.reviews_done_as_reviewer += 1
        self.object.reviewer.save()
        self.object.student.reviews_done_as_reviewee += 1
        self.object.student.save()
        return response


class ReviewDetailView(LoginRequiredMixin, DetailView):
    """
        This view is used to view info about a Review

        :cvar template_name: The template to render
        :cvar model: The model to view
        :cvar context_object_name: What name to use when passing the Review to the template
    """

    template_name = 'reviews/review_view.html'
    model = models.Review
    context_object_name = 'review'

    def get_queryset(self) -> QuerySet:
        """
            This function restricts what Reviews the user can view
            If they're an admin, they can view any completed reviews
            If they're not an admin, they can only view reviews where they are the student or reviewer

            :returns: A QuerySet defining which Reviews the user can view:
            :rtype: QuerySet
        """

        query = models.Review.objects.all()
        if self.request.user.is_superuser is False:
            query = query.filter(Q(student=self.request.user) | Q(reviewer=self.request.user))
        return query


class ReviewCompleteListView(LoginRequiredMixin, ListView):
    """
        This view lists completed reviews for the user

        :cvar template_name: The template to render
        :cvar model: The model to list
        :cvar paginate_by: How many reviews to show on each page
        :cvar context_object_name: The name to use when passing reviews to the template
    """

    template_name = "reviews/reviews_completed.html"
    model = models.Review
    paginate_by = 10
    context_object_name = 'reviews'

    def get_session(self) -> Optional[str]:
        """
            This function gets the session the instructor requested

            :returns: The session requested in the query string (if any)
            :rtype: str
        """

        session = self.request.GET.get("session", "AM")
        if session == "AM" or session == "PM":
            return session
        else:
            return None

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, object]:
        """
            This function provides additional context data to the template

            :returns: Additional context to pass to the template
            :rtype: dict
        """

        context = super(ReviewCompleteListView, self).get_context_data(object_list=object_list, **kwargs)
        if self.request.user.is_superuser:
            context['target_session'] = self.get_session()
            context['opposite_session'] = "PM" if self.get_session() == "AM" else "AM"
        return context

    def get_queryset(self) -> QuerySet:
        """
            This function limits which Reviews are listed
            If the user is an instructor, it shows all completed reviews
            Otherwise, it only shows reviews where the user is the student or reviewer

            :returns: A QuerySet defining which Reviews to list
            :rtype: QuerySet
        """

        query = models.Review.objects.filter(status=models.Review.Status.CLOSED)
        if self.request.user.is_superuser:
            session = self.get_session()
            if session is None:
                raise Http404()
            else:
                return query.filter(student__session=session)
        else:
            return query.filter(Q(student=self.request.user) | Q(reviewer=self.request.user))


# Errors


class BaseErrorView(TemplateView):
    """
        This View acts as a base for other error views

        It adds the ability to respond to POST requests so that errors still work on forms
    """

    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())


class Error404(BaseErrorView):
    """
        This view is run in the case of a 404 error
    """

    template_name = 'errors/404.html'


class Error403(BaseErrorView):
    """
        This view is run in the case of a 403 error
    """

    template_name = 'errors/403.html'


class Error500(BaseErrorView):
    """
        This view is run in the case of a 500 error
    """

    template_name = 'errors/500.html'


class Error(View):
    """
        This view is used for error pages
        If an error occurs during development, django will show a stacktrace, not an error page
        So, we use this view to see what the error pages will look like
    """

    error_dict = {
        404: Error404,
        403: Error403,
        500: Error500
    }

    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """
            This function is run when a GET request is received
            It gets the requested error page, defaulting to 404
        """

        error_type = kwargs.get('type', None)
        if error_type not in self.error_dict.keys():
            raise Http404()
        else:
            return self.error_dict.get(error_type, Error404).as_view()(request, *args, **kwargs)

    def post(self, request, *args, **kwargs) -> HttpResponse:
        """
            This function is run when the view receives a POST request
            It returns an error page
        """

        return self.get(request, *args, **kwargs)


# The following block tells django to run these views when an error occurs

error_404_handler = Error404.as_view()
error_403_handler = Error403.as_view()


def error_500_handler(request) -> HttpResponse:
    """
        This function is run in the event of a 500 error
    """

    return Error500.as_view()(request)

# Leaderboard

class LeaderboardView(LoginRequiredMixin, TemplateView):

    http_methods = ['get']
    template_name = 'reviews/leaderboard.html'

    def get_context_data(self, *args, **kwargs) -> dict[str, object]:
        context = super().get_context_data(*args, **kwargs)
        context['reviewees_dataset'] = User.objects.filter(is_superuser=False).order_by('-reviews_done_as_reviewee')
        context['reviewers_dataset'] = User.objects.filter(is_superuser=False).order_by('-reviews_done_as_reviewer')
        return context


# About

class SecretView(TemplateView):
    """
        Shhhhhhh
    """

    template_name = "about/secret.html"


class CopyrightView(TemplateView):
    """
        This view displays the services used to make the website

        :cvar template_name: The template to render
    """

    template_name = "about/copyright.html"
