from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='user_register'),
    path('login/', views.login_view, name='user_login'),
    path('logout/', views.logout_view, name='user_logout'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('bookings/', views.user_bookings, name='user_bookings'),
    path('change-password/', views.PasswordChangeView.as_view(), name='change_password'),
    path('preferences/', views.user_preferences, name='user_preferences'),
    path('update-preferences/', views.update_preferences, name='update_preferences'),
]