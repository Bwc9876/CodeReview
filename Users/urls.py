"""
    This file defines how a URL will map to a view in the Users app
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('login', views.UserLoginView.as_view(), name="login"),
    path('logout', auth_views.LogoutView.as_view(), name="logout"),
    path('logout-done', views.LogoutDoneView.as_view(), name="logout-done")
]
