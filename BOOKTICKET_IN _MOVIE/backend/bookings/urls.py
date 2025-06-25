from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('create/', views.BookingCreateView.as_view(), name='create_booking'),
    path('summary/', views.booking_summary, name='booking_summary'),
    path('<uuid:booking_id>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('<uuid:booking_id>/download/', views.download_ticket, name='download_ticket'),
    
    # Payments
    path('payments/create/', views.PaymentCreateView.as_view(), name='create_payment'),
    path('payments/<str:payment_id>/process/', views.process_payment, name='process_payment'),
    
    # Coupons
    path('coupons/validate/', views.validate_coupon, name='validate_coupon'),
    
    # Admin endpoints
    path('admin/stats/', views.admin_booking_stats, name='admin_booking_stats'),
]