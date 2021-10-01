from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name="home"),
    path('rubric', views.edit_rubric, name="rubric")
]
