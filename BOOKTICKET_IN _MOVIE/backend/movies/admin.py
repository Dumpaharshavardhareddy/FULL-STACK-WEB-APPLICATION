from django.contrib import admin
from .models import Movie, Genre, Language, MovieReview, MovieImage

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """
    Admin configuration for Genre model
    """
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """
    Admin configuration for Language model
    """
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

class MovieImageInline(admin.TabularInline):
    """
    Inline admin for MovieImage
    """
    model = MovieImage
    extra = 1

class MovieReviewInline(admin.TabularInline):
    """
    Inline admin for MovieReview
    """
    model = MovieReview
    extra = 0
    readonly_fields = ('user', 'rating', 'review', 'created_at')
    can_delete = False

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """
    Admin configuration for Movie model
    """
    list_display = ('title', 'director', 'release_date', 'rating', 'certificate', 'is_active', 'is_featured')
    list_filter = ('certificate', 'is_active', 'is_featured', 'release_date', 'genres', 'languages')
    search_fields = ('title', 'director', 'cast')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('genres', 'languages')
    date_hierarchy = 'release_date'
    inlines = [MovieImageInline, MovieReviewInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'poster')
        }),
        ('Movie Details', {
            'fields': ('director', 'cast', 'duration', 'certificate', 'genres', 'languages')
        }),
        ('Release Information', {
            'fields': ('release_date', 'end_date', 'trailer_url')
        }),
        ('Ratings & Status', {
            'fields': ('rating', 'is_active', 'is_featured')
        }),
    )

@admin.register(MovieReview)
class MovieReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for MovieReview model
    """
    list_display = ('movie', 'user', 'rating', 'is_verified', 'created_at')
    list_filter = ('rating', 'is_verified', 'created_at')
    search_fields = ('movie__title', 'user__email', 'user__first_name', 'user__last_name')
    actions = ['verify_reviews', 'unverify_reviews']
    
    def verify_reviews(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f'{queryset.count()} reviews verified successfully.')
    verify_reviews.short_description = 'Verify selected reviews'
    
    def unverify_reviews(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f'{queryset.count()} reviews unverified successfully.')
    unverify_reviews.short_description = 'Unverify selected reviews'

@admin.register(MovieImage)
class MovieImageAdmin(admin.ModelAdmin):
    """
    Admin configuration for MovieImage model
    """
    list_display = ('movie', 'caption', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('movie__title', 'caption')