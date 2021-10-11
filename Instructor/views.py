from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect

from Main import models as main_models
from Main.views import IsSuperUserMixin
from Users.models import User
from . import models, forms


class AdminHomeView(LoginRequiredMixin, IsSuperUserMixin, TemplateView):
    template_name = "admin_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = main_models.Review.objects.exclude(status=main_models.Review.Status.CLOSED)
        context['completed'] = main_models.Review.objects.filter(status=main_models.Review.Status.CLOSED)
        return context


class UserListView(LoginRequiredMixin, IsSuperUserMixin, ListView):
    template_name = "user_list.html"
    context_object_name = "users"
    model = User

    http_method_names = ['get', 'post']

    def get_queryset(self):
        return User.objects.filter(is_superuser=False)

    def post(self, *args, **kwargs):
        objs = list(self.get_queryset())
        for index, user in enumerate(objs):
            objs[index].is_reviewer = str(user.id) in self.request.POST.getlist('reviewers')
        self.get_queryset().bulk_update(objs, ['is_reviewer'], batch_size=10)
        return redirect("user-list")


# Rubrics


class RubricListView(LoginRequiredMixin, IsSuperUserMixin, ListView):
    template_name = 'rubrics/rubric_list.html'
    model = models.Rubric
    context_object_name = 'rubrics'


class RubricCreateView(LoginRequiredMixin, IsSuperUserMixin, CreateView):
    form_class = forms.RubricForm
    success_url = reverse_lazy('rubric-list')
    template_name = 'admin_form_base.html'


class RubricEditView(LoginRequiredMixin, IsSuperUserMixin, UpdateView):
    form_class = forms.RubricForm
    model = models.Rubric
    success_url = reverse_lazy('rubric-list')
    template_name = 'admin_form_base.html'


class RubricDeleteView(LoginRequiredMixin, IsSuperUserMixin, DeleteView):
    template_name = 'rubrics/rubric_delete.html'
    model = models.Rubric
    success_url = reverse_lazy('rubric-list')
