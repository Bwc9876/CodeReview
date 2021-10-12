from datetime import datetime

from django.core import mail
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, QuerySet
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, DetailView

from Users.models import User
from . import models, forms

# Email Utility Functions


def send_email(subject_template: str, text_template: str, template_name: str, review: models.Review, query_set: QuerySet):
    for user in list(query_set):
        html_content = render_to_string(template_name, {'target_user': user, 'review': review})
        text_content = text_template.format(target_user=str(user), student=str(review.student), reviewer=str(review.reviewer))
        subject = subject_template.format(target_user=str(user), student=str(review.student), reviewer=str(review.reviewer))
        message = mail.EmailMultiAlternatives(subject=subject, body=text_content)
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


# Home


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

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
            context['open'] = rubrics.filter(status=models.Review.Status.OPEN).exclude(student=user)
            context['assigned'] = rubrics.filter(status=models.Review.Status.ASSIGNED)

        return context


# Reviews


class ReviewCreateView(LoginRequiredMixin, CreateView):
    template_name = 'form_base.html'
    success_url = reverse_lazy('home')
    model = models.Review
    form_class = forms.CreateReviewForm

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
                   User.objects.filter(is_reviewer=True))
        return response


class ReviewEditView(LoginRequiredMixin, UpdateView):
    template_name = 'form_base.html'
    success_url = reverse_lazy('home')
    fields = ['schoology_id', 'rubric']
    model = models.Review

    def get_queryset(self):
        return models.Review.objects.filter(student=self.request.user).exclude(status=models.Review.Status.CLOSED)


class ReviewCancelView(LoginRequiredMixin, DeleteView):
    template_name = 'reviews/review_cancel.html'
    success_url = reverse_lazy('home')
    model = models.Review

    def get_queryset(self):
        return models.Review.objects.filter(student=self.request.user).exclude(status=models.Review.Status.CLOSED)


class ReviewDeleteView(LoginRequiredMixin, IsSuperUserMixin, DeleteView):
    template_name = 'reviews/review_delete.html'
    success_url = reverse_lazy('home')
    model = models.Review


class ReviewClaimView(LoginRequiredMixin, IsReviewerMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        target_pk = kwargs.get('pk', '')
        try:
            target_object = models.Review.objects.get(id=models.val_uuid(target_pk), status=models.Review.Status.OPEN)
            target_object.status = models.Review.Status.ASSIGNED
            target_object.reviewer = request.user
            target_object.save()
            send_email("Review accepted by {reviewer}",
                       "Hello, {target_user}, a review by {student} has been accepted by {reviewer}.",
                       "emails/review_accepted.html",
                       target_object,
                       User.objects.filter(is_superuser=True))
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
        return redirect('home')

    def get(self, *args, **kwargs) -> HttpResponse:
        target_object = self.get_target_review(kwargs.get('pk', ""))
        return render(self.request, 'reviews/review_abandon.html', {'review': target_object})


class ReviewGradeView(LoginRequiredMixin, IsReviewerMixin, UpdateView):
    template_name = 'form_base.html'
    success_url = reverse_lazy('home')
    model = models.Review
    form_class = forms.GradeReviewForm

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
