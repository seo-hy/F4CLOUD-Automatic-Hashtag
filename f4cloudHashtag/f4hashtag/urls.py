from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from f4hashtag import views

urlpatterns = [
    path('hashtag/', views.hashtag.as_view()),
    path('search/', views.search_hashtag.as_view()),

]

urlpatterns = format_suffix_patterns(urlpatterns)

