from django.urls import path

from . import views

urlpatterns = [
    path('', views.AdminHomeView.as_view(), name="instructor-home"),
    path('users/', views.UserListView.as_view(), name="user-list"),
    path('rubric/', views.RubricListView.as_view(), name="rubric-list"),
    path('rubric/create/', views.RubricCreateView.as_view(), name="rubric-create"),
    path('rubric/edit/<uuid:pk>/', views.RubricEditView.as_view(), name="rubric-edit"),
    path('rubric/delete/<uuid:pk>/', views.RubricDeleteView.as_view(), name="rubric-delete"),
]
