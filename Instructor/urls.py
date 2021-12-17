"""
    This file defines the instructor section's urls
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.AdminHomeView.as_view(), name="instructor-home"),
    path('users/', views.UserListView.as_view(), name="user-list"),
    path('users/cleanup/', views.UserClearView.as_view(), name="user-cleanup"),
    path('rubric/', views.RubricListView.as_view(), name="rubric-list"),
    path('rubric/create/', views.RubricCreateView.as_view(), name="rubric-create"),
    path('rubric/duplicate/<uuid:pk>', views.RubricDupeView.as_view(), name='rubric-duplicate'),
    path('rubric/edit/<uuid:pk>/', views.RubricEditView.as_view(), name="rubric-edit"),
    path('rubric/delete/<uuid:pk>/', views.RubricDeleteView.as_view(), name="rubric-delete"),
]
