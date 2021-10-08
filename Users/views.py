from django.shortcuts import render
from django.http import HttpResponse


def logout_done(request) -> HttpResponse:
    return render(request, "logout_complete.html")
