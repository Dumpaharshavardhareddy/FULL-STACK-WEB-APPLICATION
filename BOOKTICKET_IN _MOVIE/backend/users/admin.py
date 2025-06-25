from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for User model
    """
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'city', 'is_verified', 'is_active', 'created_at')
    list_filter = ('is_verified', 'is_active', 'is_staff', 'city', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'date_of_birth', 'city', 'is_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'city')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model
    """
    list_display = ('user', 'preferred_language', 'get_preferred_theaters_count')
    list_filter = ('preferred_language',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    
    def get_preferred_theaters_count(self, obj):
        return obj.preferred_theaters.count()
    get_preferred_theaters_count.short_description = 'Preferred Theaters'