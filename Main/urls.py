from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('rubric/', views.RubricListView.as_view(), name="rubric_list"),
    path('rubric/create/', views.RubricCreateView.as_view(), name="rubric_create"),
    path('rubric/edit/<uuid:pk>/', views.RubricEditView.as_view(), name="rubric_edit"),
    path('rubric/delete/<uuid:pk>/', views.RubricDeleteView.as_view(), name="rubric_del"),
    path('review/create/', views.ReviewCreateView.as_view(), name="review_create"),
    path('review/edit/<uuid:pk>/', views.ReviewEditView.as_view(), name="review_edit"),
    path('review/cancel/<uuid:pk>/', views.ReviewCancelView.as_view(), name="review_cancel"),
    path('review/delete/<uuid:pk>/', views.ReviewDeleteView.as_view(), name="review_delete"),
    path('review/claim/<uuid:pk>/', views.ReviewClaimView.as_view(), name="review_claim"),
    path('review/abandon/<uuid:pk>/', views.ReviewAbandonView.as_view(), name="review_abandon"),
    path('review/grade/<uuid:pk>/', views.ReviewGradeView.as_view(), name="review_grade"),
    path('review/view/<uuid:pk>/', views.ReviewDetailView.as_view(), name="review_view")
]
