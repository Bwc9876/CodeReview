from django.http import HttpResponse
from django.shortcuts import render


def logout_done(request) -> HttpResponse:
    return render(request, "logout_complete.html")
