from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name="home"),
    path('rubric/edit', views.edit_rubric, name="rubric_edit"),
    path('rubric/list', views.list_rubrics, name="rubric_list"),
    path('rubric/delete', views.delete_rubric, name="rubric_del"),
    path('review/edit', views.edit_review, name="review_edit"),
    path('review/delete', views.delete_review, name="review_delete"),
    path('review/claim', views.claim_review, name="review_claim"),
    path('review/abandon', views.abandon_review, name="review_abandon"),
    path('review/grade', views.grade_review, name="review_grade"),
    path('review/view', views.view_review, name="review_view")
]
