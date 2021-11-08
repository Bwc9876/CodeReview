"""
    This file defines how a URL will map to a view in the Users app
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('login', auth_views.LoginView.as_view(template_name="login.html", extra_context={'hide_back': True}),
         name="login"),
    path('user-setup/<uuid:pk>', views.CompleteUserSetupView.as_view(), name="user-setup"),
    path('logout', auth_views.LogoutView.as_view(), name="logout"),
    path('logout-done', views.LogoutDoneView.as_view(), name="logout-done")
]
