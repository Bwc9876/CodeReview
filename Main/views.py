from typing import Union
from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.http import require_http_methods, require_safe
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q

from . import models, forms, decorators
from Users.models import User


def super_check(user: User):
    return user.is_superuser


@require_safe
@login_required
def home_view(request) -> HttpResponse:
    user: User = request.user
    context = {
        'active': models.Review.objects.filter(student=user).exclude(status=models.Review.Status.CLOSED),
        'complete': models.Review.objects.filter((Q(student=user) | Q(reviewer=user))
                                                 & Q(status=models.Review.Status.CLOSED))
    }
    if user.is_reviewer:
        rubrics = models.Review.objects.exclude(status=models.Review.Status.CLOSED).filter(
            Q(status=models.Review.Status.OPEN, ) | Q(status=models.Review.Status.ASSIGNED, reviewer=user)
        )
        context['open'] = rubrics.filter(status=models.Review.Status.OPEN).exclude(student=user)
        context['assigned'] = rubrics.filter(status=models.Review.Status.ASSIGNED)
    return render(request, "home.html", context)


@require_http_methods(['GET', 'POST'])
@login_required
@user_passes_test(super_check)
def edit_rubric(request) -> Union[HttpResponse, HttpResponseRedirect]:
    current_id: str = request.GET.get("id", "")
    if request.method == "GET":
        if current_id == "":
            form = forms.RubricForm()
        else:
            current_rubric = get_object_or_404(models.Rubric, id=models.val_uuid(current_id))
            form = forms.RubricForm({'name': current_rubric.name, 'rubric': current_rubric.to_json()})
        return render(request, 'form_base.html', {'form': form})
    elif request.method == "POST":
        form = forms.RubricForm(request.POST)
        if form.is_valid():
            current_id: str = request.GET.get("id", None)
            data = form.cleaned_data
            models.Rubric.create_from_json(data.get("name"), data.get("rubric"), current_id=models.val_uuid(current_id))
            return redirect("rubric_list")
        else:
            return render(request, 'form_base.html', {'form': form})


@require_http_methods(['GET', 'POST'])
@login_required
@user_passes_test(super_check)
def delete_rubric(request) -> Union[HttpResponse, HttpResponseRedirect]:
    target_id = request.GET.get("id", "")
    target_object = get_object_or_404(models.Rubric, id=models.val_uuid(target_id))
    if request.method == "GET":
        return render(request, "rubrics/rubric_del.html", {'rubric': target_object})
    else:
        target_object.delete()
        return redirect("rubric_list")


@require_safe
@login_required
@user_passes_test(super_check)
def list_rubrics(request) -> HttpResponse:
    rubrics = models.Rubric.objects.all()
    return render(request, "rubrics/rubric_list.html", {'rubrics': rubrics})


@require_http_methods(['GET', 'POST'])
@login_required
@decorators.review_require_student()
@decorators.review_require_status(status=models.Review.Status.OPEN)
def delete_review(request) -> Union[HttpResponse, HttpResponseRedirect]:
    target_id = request.GET.get("id", "")
    target_object = get_object_or_404(models.Review, id=models.val_uuid(target_id))
    if request.method == "GET":
        return render(request, "reviews/review_del.html", {'review': target_object})
    else:
        target_object.delete()
        return redirect("home")


@require_http_methods(['GET', 'POST'])
@login_required
@decorators.review_require_either(allow_404=True)
def edit_review(request) -> Union[HttpResponse, HttpResponseRedirect]:
    current_id = request.GET.get("id", "")
    if request.method == "GET":
        if current_id == "":
            form = forms.CreateReviewForm()
        else:
            form = forms.CreateReviewForm(instance=get_object_or_404(models.Review, id=models.val_uuid(current_id)))
        return render(request, "form_base.html", {'form': form})
    else:
        if current_id == "":
            form = forms.CreateReviewForm(request.POST)
        else:
            form = forms.CreateReviewForm(request.POST,
                                          instance=get_object_or_404(models.Review, id=models.val_uuid(current_id)))
        if form.is_valid():
            new_review: models.Review = form.save(commit=False)
            new_review.student = request.user
            new_review.status = models.Review.Status.OPEN
            new_review.save()
            if current_id == "":
                # TODO: Send email
                pass
            return redirect("home")
        else:
            return render(request, "form_base.html", {'form': form})


@require_http_methods(["POST"])
@login_required
@decorators.review_require_status(status=models.Review.Status.OPEN)
def claim_review(request) -> HttpResponseRedirect:
    user: User = request.user
    if user.is_reviewer:
        target_id = request.GET.get("id", "")
        target_object = get_object_or_404(models.Review, id=models.val_uuid(target_id))
        target_object.status = models.Review.Status.ASSIGNED
        target_object.reviewer = user
        target_object.save()
        # TODO: Send email
        return redirect("home")
    else:
        raise Http404()


@require_http_methods(["GET", "POST"])
@login_required
@decorators.review_require_reviewer()
@decorators.review_require_status(models.Review.Status.ASSIGNED)
def abandon_review(request) -> Union[HttpResponse, HttpResponseRedirect]:
    target_id = request.GET.get("id", "")
    target_object = get_object_or_404(models.Review, id=models.val_uuid(target_id))
    if target_object.status == int(models.Review.Status.ASSIGNED):
        if target_object.reviewer == request.user or request.user.is_superuser:
            if request.method == 'GET':
                return render(request, 'reviews/review_abandon.html', {'review': target_object})
            else:
                target_object.status = models.Review.Status.OPEN
                target_object.reviewer = None
                target_object.save()
                return redirect("home")
        else:
            raise Http404()
    else:
        raise Http404()


@require_http_methods(["GET", "POST"])
@login_required
@decorators.review_require_reviewer()
@decorators.review_require_status(models.Review.Status.ASSIGNED)
def grade_review(request) -> Union[HttpResponse, HttpResponseRedirect]:
    target_id = request.GET.get("id", "")
    target_object = get_object_or_404(models.Review, id=models.val_uuid(target_id))
    if target_object.reviewer == request.user or request.user.is_superuser:
        if request.method == "GET":
            form = forms.GradeReviewForm(instance=target_object)
            form.set_rubric(target_object.rubric)
            return render(request, "form_base.html", {'form': form})
        else:
            form = forms.GradeReviewForm(request.POST, instance=target_object)
            form.set_rubric(target_object.rubric)
            if form.is_valid():
                new_object: models.Review = form.save(commit=False)
                new_object.date_completed = datetime.now()
                new_object.status = models.Review.Status.CLOSED
                new_object.save()
                # TODO: Send email
                return redirect("home")
            else:
                return render(request, "form_base.html", {'form': form})
    else:
        raise Http404()


@require_safe
@login_required
@decorators.review_require_either(allow_404=False)
@decorators.review_require_status(models.Review.Status.CLOSED)
def view_review(request) -> HttpResponse:
    target_id = request.GET.get('id', "")
    target_object = get_object_or_404(models.Review, id=models.val_uuid(target_id))
    if target_object.status == int(models.Review.Status.CLOSED):
        return render(request, "reviews/review_view.html", {'review': target_object})
    else:
        raise Http404()
