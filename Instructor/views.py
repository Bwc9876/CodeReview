from json import JSONDecoder, JSONDecodeError

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView
from jsonschema import validate
from jsonschema.exceptions import ValidationError as JsonValidationError

from Main import models as main_models
from Main.views import IsSuperUserMixin, FormNameMixin, FormAlertMixin, SuccessDeleteMixin
from Users.models import User
from . import models, forms


class AdminHomeView(LoginRequiredMixin, IsSuperUserMixin, TemplateView):
    template_name = "admin_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active = main_models.Review.objects.exclude(status=main_models.Review.Status.CLOSED)
        completed = main_models.Review.objects.filter(status=main_models.Review.Status.CLOSED)
        context['am_active'] = active.filter(student__session=User.Session.AM)
        context['am_completed'] = completed.filter(student__session=User.Session.AM)
        context['pm_active'] = active.filter(student__session=User.Session.PM)
        context['pm_completed'] = completed.filter(student__session=User.Session.PM)
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
        messages.add_message(self.request, messages.SUCCESS, "Users Updated")
        return redirect("instructor-home")

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


class RubricCreateView(LoginRequiredMixin, IsSuperUserMixin, FormNameMixin, FormAlertMixin, CreateView):
    form_class = forms.RubricForm
    success_url = reverse_lazy('rubric-list')
    template_name = 'form_base.html'
    form_name = "Create Rubric"
    success_message = "New Rubric Saved"


class RubricEditView(LoginRequiredMixin, IsSuperUserMixin, FormNameMixin, FormAlertMixin, UpdateView):
    form_class = forms.RubricForm
    form_name = "Edit Rubric"
    model = models.Rubric
    success_url = reverse_lazy('rubric-list')
    template_name = 'form_base.html'
    success_message = "Rubric Updated"


class RubricDeleteView(LoginRequiredMixin, IsSuperUserMixin, SuccessDeleteMixin, DeleteView):
    template_name = 'rubrics/rubric_delete.html'
    model = models.Rubric
    success_url = reverse_lazy('rubric-list')
    success_message = "Rubric Deleted"

    def get_context_data(self, **kwargs):
        context = super(RubricDeleteView, self).get_context_data(**kwargs)
        context['objectString'] = self.object.name
        return context
