"""
    This file defines middleware, which is code that runs before a view
"""

from django.shortcuts import redirect
from django.conf import settings


class UserSetupCheckMiddleware:
    """
        This middleware will redirect the user to the user setup page if they're from IIS and need a student_id
    """

    def __init__(self, get_response):
        """
            This function is run to create a new instance of the middleware

            :param: get_response: A function that gets the response for this request
        """

        self.get_response = get_response

    def __call__(self, request):
        """
            This method is run when calling the middleware
            If the user doesn't have a student_id, require them to enter one
        """

        if "user-setup" not in request.path and request.user.is_authenticated and (request.user.has_usable_password() or settings.DEBUG) and request.user.student_id is None:
            return redirect('user-setup', pk=request.user.id)
        else:
            return self.get_response(request)
