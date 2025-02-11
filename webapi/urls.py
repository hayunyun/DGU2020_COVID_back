import django.urls as dur

from . import views


urlpatterns = [
    dur.path("echo/", views.Echo.as_view()),
    dur.path("get_similar_seq_ids/", views.GetSimilarSeqIDs.as_view()),
    dur.path("get_metadata_of_seq/", views.GetMetadataOfSeq.as_view()),
    dur.path("calc_similarity_of_two_seq/", views.CalcSimilarityOfTwoSeq.as_view()),
    dur.path("get_all_acc_ids/", views.GetAllAccIDs.as_view()),
    dur.path("find_mutations/", views.FindMutations.as_view()),

    dur.path("num_cases_per_division/", views.NumCasesPerDivision.as_view()),
    dur.path("num_cases_per_country/", views.NumCasesPerCountry.as_view()),
]
