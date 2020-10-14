import django.urls as dur

from . import views


urlpatterns = [
    dur.path('testlist/', views.TestList.as_view()),
]
