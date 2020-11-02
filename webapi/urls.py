from django.urls import path
from . import views


urlpatterns = [
    path('testlist/', views.TestList.as_view()),
    path("echo/", views.Echo.as_view()),
    path("get_similar_seq_ids/", views.SimilarSeqIDs.as_view()),
]
