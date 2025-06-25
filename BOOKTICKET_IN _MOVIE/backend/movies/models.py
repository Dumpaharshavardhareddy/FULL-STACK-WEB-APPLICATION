from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

class Genre(models.Model):
    """
    Model for movie genres
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'genres'
        ordering = ['name']

class Language(models.Model):
    """
    Model for movie languages
    """
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)  # e.g., 'en', 'hi', 'ta'
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'languages'
        ordering = ['name']

class Movie(models.Model):
    """
    Model for movies
    """
    RATING_CHOICES = [
        ('U', 'U - Universal'),
        ('UA', 'UA - Parental Guidance'),
        ('A', 'A - Adults Only'),
        ('S', 'S - Restricted'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    release_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Last show date")
    
    # Movie details
    director = models.CharField(max_length=100)
    cast = models.TextField(help_text="Main cast members, comma separated")
    genres = models.ManyToManyField(Genre, related_name='movies')
    languages = models.ManyToManyField(Language, related_name='movies')
    
    # Ratings and reviews
    rating = models.DecimalField(
        max_digits=3, decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0.0
    )
    certificate = models.CharField(max_length=5, choices=RATING_CHOICES, default='U')
    
    # Media
    poster = models.ImageField(upload_to='movies/posters/')
    trailer_url = models.URLField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.release_date.year})"
    
    @property
    def duration_formatted(self):
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    @property
    def genre_list(self):
        return list(self.genres.values_list('name', flat=True))
    
    @property
    def language_list(self):
        return list(self.languages.values_list('name', flat=True))
    
    @property
    def cast_list(self):
        return [name.strip() for name in self.cast.split(',') if name.strip()]
    
    class Meta:
        db_table = 'movies'
        ordering = ['-release_date', 'title']
        indexes = [
            models.Index(fields=['release_date']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
        ]

class MovieReview(models.Model):
    """
    Model for movie reviews by users
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.movie.title} - {self.user.full_name} ({self.rating}/5)"
    
    class Meta:
        db_table = 'movie_reviews'
        unique_together = ('movie', 'user')
        ordering = ['-created_at']

class MovieImage(models.Model):
    """
    Model for additional movie images
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='movies/images/')
    caption = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.movie.title} - Image"
    
    class Meta:
        db_table = 'movie_images'
        ordering = ['-is_featured', '-created_at']