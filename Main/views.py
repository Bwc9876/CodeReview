from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core import mail
from django.db.models import Q, QuerySet
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
    for user in list(query_set):
        html_content = render_to_string(template_name, {'target_user': user, 'review': review})
        text_content = text_template.format(target_user=str(user), student=str(review.student),
                                            reviewer=str(review.reviewer))
        subject = subject_template.format(target_user=str(user), student=str(review.student),
                                          reviewer=str(review.reviewer))
        message = mail.EmailMultiAlternatives(subject=f'{review.student.session} | {subject}', body=text_content)
        message.attach_alternative(html_content, "text/html")
        message.to = [user.email]
        message.send(fail_silently=False)


# Mixins


class IsSuperUserMixin(UserPassesTestMixin):
    request = None

    def test_func(self):
        return self.request.user.is_superuser


class IsReviewerMixin(UserPassesTestMixin):
    request = None

    def test_func(self):
        return self.request.user.is_reviewer


class FormNameMixin(ContextMixin):
    form_name = "Form"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formName'] = self.form_name
        return context


class FormAlertMixin(FormMixin):
    request = None

    success_message: str = "Complete"
    failure_message: str = "The information you provided was incorrect, please correct the following errors"

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, self.success_message)
        return super(FormAlertMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, self.failure_message)
        return super(FormAlertMixin, self).form_invalid(form)


class SuccessDeleteMixin(DeletionMixin):
    success_message: str = "Deleted"

    def delete(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, self.success_message)
        return super(SuccessDeleteMixin, self).delete(request, *args, **kwargs)


# Home


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get(self, *args, **kwargs):
        if self.request.user.is_superuser:
            return redirect('instructor-home')
        else:
            return super(HomeView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
    template_name = 'form_base.html'
    success_url = reverse_lazy('home')
    model = models.Review
    form_class = forms.CreateReviewForm
    form_name = "Create a Review"
    success_message = "New Review Saved"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super(ReviewCreateView, self).form_valid(form)
        send_email("Review created by {student}",
                   "Hello {target_user}, a new review has been created by {student}",
                   "emails/review_created.html",
                   self.object,
                   User.objects.filter(is_reviewer=True, session=self.request.user.session).exclude(
                       id=self.request.user.id))
        return response


class ReviewEditView(LoginRequiredMixin, FormNameMixin, FormAlertMixin, UpdateView):
    template_name = 'form_base.html'
    success_url = reverse_lazy('home')
    fields = ['schoology_id', 'rubric']
    model = models.Review
    form_name = "Edit Review"
    success_message = "Review Updated"

    def get_queryset(self):
        return models.Review.objects.filter(student=self.request.user).exclude(status=models.Review.Status.CLOSED)


class ReviewCancelView(LoginRequiredMixin, SuccessDeleteMixin, DeleteView):
    template_name = 'reviews/review_cancel.html'
    success_url = reverse_lazy('home')
    model = models.Review
    success_message = "Review Cancelled"

    def get_context_data(self, **kwargs):
        context = super(ReviewCancelView, self).get_context_data(**kwargs)
        context['objectString'] = f"review with schoology id: {self.object.schoology_id}"
        return context

    def get_queryset(self):
        return models.Review.objects.filter(student=self.request.user).exclude(status=models.Review.Status.CLOSED)


class ReviewDeleteView(LoginRequiredMixin, IsSuperUserMixin, SuccessDeleteMixin, DeleteView):
    template_name = 'reviews/review_delete.html'
    success_url = reverse_lazy('home')
    model = models.Review
    success_message = "Review Deleted"

    def get_context_data(self, **kwargs):
        context = super(ReviewDeleteView, self).get_context_data(**kwargs)
        context['objectString'] = f"review from {self.object.student}"
        return context


class ReviewClaimView(LoginRequiredMixin, IsReviewerMixin, View):

    def post(self, request, *args, **kwargs):
        target_pk = kwargs.get('pk', '')
        try:
            target_object = models.Review.objects.get(id=models.val_uuid(target_pk), status=models.Review.Status.OPEN,
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

    def get_target_review(self, target_id: str) -> models.Review:
        try:
            return models.Review.objects.get(id=models.val_uuid(target_id),
                                             status=models.Review.Status.ASSIGNED, reviewer=self.request.user)
        except models.Review.DoesNotExist:
            raise Http404


class ReviewAbandonView(ReviewerAction):
    http_method_names = ['get', 'post']

    def post(self, *args, **kwargs) -> HttpResponseRedirect:
        target_object = self.get_target_review(kwargs.get('pk', ""))
        target_object.status = models.Review.Status.OPEN
        target_object.reviewer = None
        target_object.save()
        messages.add_message(self.request, messages.SUCCESS, "Review Abandoned")
        return redirect('home')

    def get(self, *args, **kwargs) -> HttpResponse:
        target_object = self.get_target_review(kwargs.get('pk', ""))
        return render(self.request, 'reviews/review_abandon.html', {'review': target_object,
                                                                    'objectString': f"review with {target_object.student}"})


class ReviewGradeView(LoginRequiredMixin, IsReviewerMixin, FormNameMixin, FormAlertMixin, UpdateView):
    template_name = 'form_base.html'
    success_url = reverse_lazy('home')
    model = models.Review
    form_class = forms.GradeReviewForm
    form_name = "Grade Review"
    success_message = "Review Graded"

    def get_queryset(self):
        return models.Review.objects.filter(reviewer=self.request.user, status=models.Review.Status.ASSIGNED)

    def form_valid(self, form):
        self.object.date_completed = datetime.now()
        self.object.save()
        send_email("Review completed by {reviewer}",
                   "Hello, {target_user}, the review requested by {student} has been completed by {reviewer}.",
                   "emails/review_completed.html",
                   self.object,
                   User.objects.filter(is_superuser=True))
        return super().form_valid(form)


class ReviewDetailView(LoginRequiredMixin, DetailView):
    template_name = 'reviews/review_view.html'
    model = models.Review
    context_object_name = 'review'

    def get_queryset(self):
        query = models.Review.objects.filter(status=models.Review.Status.CLOSED)
        if not self.request.user.is_superuser:
            query = query.filter(Q(student=self.request.user) | Q(reviewer=self.request.user))
        return query


class ReviewCompleteListView(LoginRequiredMixin, ListView):
    template_name = "reviews/reviews_completed.html"
    model = models.Review
    paginate_by = 10
    context_object_name = 'reviews'

    def get_session(self):
        session = self.request.GET.get("session", "AM")
        if session == "AM" or session == "PM":
            return session
        else:
            return None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ReviewCompleteListView, self).get_context_data(object_list=object_list, **kwargs)
        if self.request.user.is_superuser:
            context['target_session'] = self.get_session()
            context['opposite_session'] = "PM" if self.get_session() == "AM" else "AM"
        return context

    def get_queryset(self):
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


class Error404(TemplateView):
    template_name = 'errors/404.html'


class Error403(TemplateView):
    template_name = 'errors/403.html'


class Error500(TemplateView):
    template_name = 'errors/500.html'


class TestError(View):

    error_dict = {
        '404': Error404,
        '403': Error403,
        '500': Error500
    }

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        error_type = request.GET.get("type", "404")
        return self.error_dict.get(error_type, Error404).as_view()(request, *args, **kwargs)


error_404_handler = Error404.as_view()
error_403_handler = Error403.as_view()


def error_500_handler(request):
    return Error500.as_view()(request)
