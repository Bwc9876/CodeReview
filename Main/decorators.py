from django.http import Http404
from django.shortcuts import get_object_or_404

from Main import models


def review_require_either(allow_404=True):
    def wrapper(func):
        def inner(request):
            target_id = request.GET.get("id", "")
            try:
                target = get_object_or_404(models.Review, id=models.val_uuid(target_id))
                affiliated = target.affiliated(request.user)
            except Http404:
                affiliated = allow_404
            if affiliated:
                return func(request)
            else:
                raise Http404("The requested Review was not found")

        return inner

    return wrapper


def review_require_reviewer():
    def wrapper(func):
        def inner(request):
            if request.user.is_superuser:
                return func(request)
            target_id = request.GET.get("id", "")
            target = get_object_or_404(models.Review, id=models.val_uuid(target_id), reviewer=request.user)
            return func(request)

        return inner

    return wrapper


def review_require_student():
    def wrapper(func):
        def inner(request):
            if request.user.is_superuser:
                return func(request)
            target_id = request.GET.get("id", "")
            target = get_object_or_404(models.Review, id=models.val_uuid(target_id), student=request.user)
            return func(request)

        return inner

    return wrapper


def review_require_status(status=models.Review.Status.OPEN):
    def wrapper(func):
        def inner(request):
            target_id = request.GET.get("id", "")
            target = get_object_or_404(models.Review, id=models.val_uuid(target_id), status=status)
            return func(request)

        return inner

    return wrapper
