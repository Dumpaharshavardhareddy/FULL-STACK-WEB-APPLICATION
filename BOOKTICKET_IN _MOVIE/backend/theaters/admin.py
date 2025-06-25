from django.contrib import admin
from .models import Theater, Screen, Show, Seat, SeatCategory, ShowSeatPricing

@admin.register(SeatCategory)
class SeatCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for SeatCategory model
    """
    list_display = ('name', 'description', 'color_code')
    search_fields = ('name',)

class ScreenInline(admin.TabularInline):
    """
    Inline admin for Screen
    """
    model = Screen
    extra = 1

class SeatInline(admin.TabularInline):
    """
    Inline admin for Seat
    """
    model = Seat
    extra = 0

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    """
    Admin configuration for Theater model
    """
    list_display = ('name', 'city', 'state', 'total_screens', 'is_active')
    list_filter = ('city', 'state', 'is_active')
    search_fields = ('name', 'city', 'address')
    inlines = [ScreenInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'city', 'state', 'pincode')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
        ('Theater Details', {
            'fields': ('total_screens', 'facilities')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    """
    Admin configuration for Screen model
    """
    list_display = ('name', 'theater', 'screen_type', 'total_seats', 'is_active')
    list_filter = ('screen_type', 'is_active', 'theater__city')
    search_fields = ('name', 'theater__name')
    inlines = [SeatInline]

class ShowSeatPricingInline(admin.TabularInline):
    """
    Inline admin for ShowSeatPricing
    """
    model = ShowSeatPricing
    extra = 1

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    """
    Admin configuration for Show model
    """
    list_display = ('movie', 'screen', 'show_date', 'show_time', 'base_price', 'available_seats', 'is_active')
    list_filter = ('show_date', 'is_active', 'is_housefull', 'screen__theater__city')
    search_fields = ('movie__title', 'screen__name', 'screen__theater__name')
    date_hierarchy = 'show_date'
    inlines = [ShowSeatPricingInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('movie', 'screen', 'screen__theater')

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    """
    Admin configuration for Seat model
    """
    list_display = ('seat_number', 'screen', 'row', 'column', 'category', 'is_active')
    list_filter = ('category', 'is_active', 'is_accessible', 'screen__theater__city')
    search_fields = ('seat_number', 'screen__name', 'screen__theater__name')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('screen', 'screen__theater', 'category')

@admin.register(ShowSeatPricing)
class ShowSeatPricingAdmin(admin.ModelAdmin):
    """
    Admin configuration for ShowSeatPricing model
    """
    list_display = ('show', 'seat_category', 'price')
    list_filter = ('seat_category', 'show__show_date')
    search_fields = ('show__movie__title', 'seat_category__name')