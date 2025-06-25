from django.urls import path
from . import views

urlpatterns = [
    path('', views.TheaterListView.as_view(), name='theater_list'),
    path('cities/', views.cities_list, name='cities_list'),
    path('city/<str:city>/', views.theaters_by_city, name='theaters_by_city'),
    path('<int:pk>/', views.TheaterDetailView.as_view(), name='theater_detail'),
    
    # Shows
    path('shows/', views.ShowListView.as_view(), name='show_list'),
    path('shows/<int:pk>/', views.ShowDetailView.as_view(), name='show_detail'),
    path('shows/movie/<int:movie_id>/', views.shows_by_movie_and_city, name='shows_by_movie'),
    path('shows/<int:show_id>/seats/', views.seat_layout, name='seat_layout'),
    
    # Admin endpoints
    path('shows/create/', views.ShowCreateView.as_view(), name='create_show'),
    path('shows/bulk-create/', views.bulk_create_shows, name='bulk_create_shows'),
]