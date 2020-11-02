from django.urls import path
from . import views


urlpatterns = [
<<<<<<< HEAD
<<<<<<< HEAD
    path('testlist/', views.TestList.as_view()),
    path("echo/", views.Echo.as_view()),
    path("get_similar_seq_ids/", views.SimilarSeqIDs.as_view()),
=======
=======
>>>>>>> 171a8c111c225ded5026786f103771f2c0a174cf
    dur.path("echo/", views.Echo.as_view()),
    dur.path("get_similar_seq_ids/", views.GetSimilarSeqIDs.as_view()),
    dur.path("get_metadata_of_seq/", views.GetMetadataOfSeq.as_view()),
    dur.path("calc_similarity_of_two_seq/", views.CalcSimilarityOfTwoSeq.as_view()),
<<<<<<< HEAD
>>>>>>> 171a8c111c225ded5026786f103771f2c0a174cf
=======
>>>>>>> 171a8c111c225ded5026786f103771f2c0a174cf
]
