from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, BookedSeat, Payment, Coupon, CouponUsage

class BookedSeatInline(admin.TabularInline):
    """
    Inline admin for BookedSeat
    """
    model = BookedSeat
    extra = 0
    readonly_fields = ('seat', 'price')

class PaymentInline(admin.StackedInline):
    """
    Inline admin for Payment
    """
    model = Payment
    extra = 0
    readonly_fields = ('payment_id', 'initiated_at', 'completed_at', 'failed_at')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin configuration for Booking model
    """
    list_display = (
        'booking_id', 'user', 'movie_title', 'theater_name',
        'show_date', 'quantity', 'final_amount', 'status', 'payment_status'
    )
    list_filter = (
        'status', 'payment_status', 'show__show_date',
        'show__screen__theater__city', 'booking_time'
    )
    search_fields = (
        'booking_id', 'user__email', 'user__first_name', 'user__last_name',
        'show__movie__title', 'phone_number', 'email'
    )
    readonly_fields = ('booking_id', 'booking_time', 'expiry_time', 'is_expired')
    inlines = [BookedSeatInline, PaymentInline]
    date_hierarchy = 'booking_time'
    
    def show_date(self, obj):
        return obj.show.show_date
    show_date.short_description = 'Show Date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'show', 'show__movie', 'show__screen', 'show__screen__theater'
        )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Payment model
    """
    list_display = (
        'payment_id', 'booking', 'payment_method', 'amount',
        'status', 'initiated_at', 'completed_at'
    )
    list_filter = ('payment_method', 'status', 'initiated_at')
    search_fields = ('payment_id', 'booking__booking_id', 'gateway_transaction_id')
    readonly_fields = ('payment_id', 'initiated_at', 'completed_at', 'failed_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking', 'booking__user')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """
    Admin configuration for Coupon model
    """
    list_display = (
        'code', 'description', 'coupon_type', 'value',
        'used_count', 'usage_limit', 'is_valid_display', 'is_active'
    )
    list_filter = ('coupon_type', 'is_active', 'valid_from', 'valid_until')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count', 'is_valid')
    
    def is_valid_display(self, obj):
        if obj.is_valid:
            return format_html('<span style="color: green;">✓ Valid</span>')
        else:
            return format_html('<span style="color: red;">✗ Invalid</span>')
    is_valid_display.short_description = 'Valid'

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    """
    Admin configuration for CouponUsage model
    """
    list_display = ('coupon', 'user', 'booking', 'discount_amount', 'used_at')
    list_filter = ('used_at', 'coupon')
    search_fields = ('coupon__code', 'user__email', 'booking__booking_id')
    readonly_fields = ('used_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('coupon', 'user', 'booking')