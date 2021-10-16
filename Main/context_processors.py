from django.conf import settings
from django.http import HttpRequest

from Users.models import User


def base_context(request: HttpRequest) -> dict:
    user: User = request.user
    return {
        'debug': settings.DEBUG,
        'base_template': "admin_base.html" if user.is_superuser else "base.html"
    }
