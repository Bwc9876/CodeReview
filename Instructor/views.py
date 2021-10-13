from json import JSONDecoder, JSONDecodeError

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView
from django.http import Http404
from django.shortcuts import redirect
from jsonschema import validate
from jsonschema.exceptions import ValidationError as JsonValidationError

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


class UserListView(LoginRequiredMixin, IsSuperUserMixin, TemplateView):
    template_name = "user_list.html"
    http_method_names = ['get', 'post']

    _schema = {
        'type': "object",
        'properties': {
            'AM': {
                'type': "array",
                'items': {
                    'type': "string"
                }
            },
            'PM': {
                'type': "array",
                'items': {
                    'type': "string"
                }
            }
        }
    }

    def get_queryset(self):
        return User.objects.filter(is_superuser=False)

    def update_sessions(self, sessions_json, objs):
        try:
            sessions = JSONDecoder().decode(sessions_json)
            validate(sessions, self._schema)
            for user_id in sessions['AM']:
                user = User.objects.get(id=main_models.val_uuid(user_id))
                objs[objs.index(user)].session = User.Session.AM
            for user_id in sessions['PM']:
                user = User.objects.get(id=main_models.val_uuid(user_id))
                objs[objs.index(user)].session = User.Session.PM
            self.get_queryset().bulk_update(objs, ['session'], batch_size=10)
        except User.DoesNotExist:
            raise Http404('Invalid Data')
        except JSONDecodeError:
            raise Http404('Invalid Data')
        except JsonValidationError:
            raise Http404('Invalid Data')

    def post(self, *args, **kwargs):
        objs = list(self.get_queryset())
        for index, user in enumerate(objs):
            objs[index].is_reviewer = str(user.id) in self.request.POST.getlist('reviewers')
        self.get_queryset().bulk_update(objs, ['is_reviewer'], batch_size=10)
        self.update_sessions(self.request.POST.get("sessions"), objs)
        return redirect("user-list")

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['AM'] = self.get_queryset().filter(session=User.Session.AM)
        context['PM'] = self.get_queryset().filter(session=User.Session.PM)
        return context


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
