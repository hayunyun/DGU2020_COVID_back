import django.urls as dur

from . import views


urlpatterns = [
    dur.path('testlist/', views.TestList.as_view()),
    dur.path("echo/", views.Echo.as_view()),
    dur.path("similar_seq_ids/", views.SimilarSeqIDs.as_view()),
]
