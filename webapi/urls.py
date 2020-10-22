import django.urls as dur

from . import views


urlpatterns = [
    dur.path("echo/", views.Echo.as_view()),
    dur.path("similar_seq_ids/", views.SimilarSeqIDs.as_view()),
    dur.path("get_similar_seq_ids/", views.GetSimilarSeqIDs.as_view())
]
