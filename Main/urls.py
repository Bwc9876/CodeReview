"""
    This file defines the main section's urls
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('review/create/', views.ReviewCreateView.as_view(), name="review-create"),
    path('review/edit/<uuid:pk>/', views.ReviewEditView.as_view(), name="review-edit"),
    path('review/cancel/<uuid:pk>/', views.ReviewCancelView.as_view(), name="review-cancel"),
    path('review/delete/<uuid:pk>/', views.ReviewDeleteView.as_view(), name="review-delete"),
    path('review/claim/<uuid:pk>/', views.ReviewClaimView.as_view(), name="review-claim"),
    path('review/abandon/<uuid:pk>/', views.ReviewAbandonView.as_view(), name="review-abandon"),
    path('review/grade/<uuid:pk>/', views.ReviewGradeView.as_view(), name="review-grade"),
    path('review/view/<uuid:pk>/', views.ReviewDetailView.as_view(), name="review-view"),
    path('review/completed/', views.ReviewCompleteListView.as_view(), name="review-complete"),
    path('secret/', views.SecretView.as_view(), name='secret'),
    path('copyright/', views.CopyrightView.as_view(), name="copyright"),
    path('error/<int:type>/', views.Error.as_view(), name='error')
]
