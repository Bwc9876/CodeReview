from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('login', auth_views.LoginView.as_view(template_name="login.html", extra_context={'hide_back': True}), name="login"),
    path('logout', auth_views.LogoutView.as_view(), name="logout"),
    path('logout-done', views.logout_done, name="logout-done")
]
