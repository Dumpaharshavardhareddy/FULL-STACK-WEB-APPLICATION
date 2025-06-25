from django.urls import path
from . import views

urlpatterns = [
    path('', views.MovieListView.as_view(), name='movie_list'),
    path('featured/', views.FeaturedMoviesView.as_view(), name='featured_movies'),
    path('nowshowing/', views.NowShowingMoviesView.as_view(), name='nowshowing_movies'),
    path('upcoming/', views.UpcomingMoviesView.as_view(), name='upcoming_movies'),
    path('genres/', views.genres_list, name='genres_list'),
    path('languages/', views.languages_list, name='languages_list'),
    path('search/', views.movie_search, name='movie_search'),
    path('theater/<int:theater_id>/', views.movie_by_theater, name='movie_by_theater'),
    path('<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('<int:movie_id>/reviews/', views.MovieReviewListView.as_view(), name='movie_reviews'),
    path('reviews/create/', views.MovieReviewCreateView.as_view(), name='create_review'),
]