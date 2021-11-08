from django.shortcuts import redirect
from django.conf import settings


class UserSetupCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "user-setup" not in request.path and request.user.is_authenticated and (request.user.has_usable_password() or settings.DEBUG) and request.user.student_id is None:
            return redirect('user-setup', pk=request.user.id)
        else:
            return self.get_response(request)
