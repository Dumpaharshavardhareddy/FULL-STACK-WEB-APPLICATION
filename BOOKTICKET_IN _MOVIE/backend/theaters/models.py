from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Theater(models.Model):
    """
    Model for movie theaters
    """
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    
    # Theater details
    total_screens = models.PositiveIntegerField(default=1)
    facilities = models.JSONField(default=list, help_text="List of facilities like ['Parking', 'Food Court', 'AC']")
    
    # Location
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name}, {self.city}"
    
    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state} - {self.pincode}"
    
    class Meta:
        db_table = 'theaters'
        ordering = ['city', 'name']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['is_active']),
        ]

class Screen(models.Model):
    """
    Model for theater screens
    """
    SCREEN_TYPES = [
        ('2D', '2D'),
        ('3D', '3D'),
        ('IMAX', 'IMAX'),
        ('4DX', '4DX'),
        ('DOLBY', 'Dolby Atmos'),
    ]
    
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='screens')
    name = models.CharField(max_length=100)  # e.g., "Screen 1", "Audi 1"
    screen_type = models.CharField(max_length=10, choices=SCREEN_TYPES, default='2D')
    total_seats = models.PositiveIntegerField()
    
    # Seat configuration
    rows = models.PositiveIntegerField(default=10)
    seats_per_row = models.PositiveIntegerField(default=15)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.theater.name} - {self.name}"
    
    class Meta:
        db_table = 'screens'
        unique_together = ('theater', 'name')
        ordering = ['theater', 'name']

class SeatCategory(models.Model):
    """
    Model for seat categories (e.g., Premium, Gold, Silver)
    """
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, default='#007bff')  # Hex color code
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'seat_categories'
        verbose_name_plural = 'Seat Categories'

class Seat(models.Model):
    """
    Model for individual seats in a screen
    """
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)  # e.g., "A1", "B5"
    row = models.CharField(max_length=5)  # e.g., "A", "B", "C"
    column = models.PositiveIntegerField()  # e.g., 1, 2, 3
    category = models.ForeignKey(SeatCategory, on_delete=models.CASCADE)
    
    # Seat properties
    is_active = models.BooleanField(default=True)
    is_accessible = models.BooleanField(default=False)  # For disabled access
    
    def __str__(self):
        return f"{self.screen} - {self.seat_number}"
    
    class Meta:
        db_table = 'seats'
        unique_together = ('screen', 'seat_number')
        ordering = ['screen', 'row', 'column']

class Show(models.Model):
    """
    Model for movie shows
    """
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, related_name='shows')
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='shows')
    show_date = models.DateField()
    show_time = models.TimeField()
    
    # Pricing
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_housefull = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.movie.title} - {self.screen} - {self.show_date} {self.show_time}"
    
    @property
    def theater(self):
        return self.screen.theater
    
    @property
    def available_seats(self):
        total_seats = self.screen.total_seats
        booked_seats = self.bookings.filter(status='confirmed').aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        return total_seats - booked_seats
    
    @property
    def is_past(self):
        from django.utils import timezone
        show_datetime = timezone.datetime.combine(self.show_date, self.show_time)
        return timezone.make_aware(show_datetime) < timezone.now()
    
    class Meta:
        db_table = 'shows'
        unique_together = ('screen', 'show_date', 'show_time')
        ordering = ['show_date', 'show_time']
        indexes = [
            models.Index(fields=['show_date', 'show_time']),
            models.Index(fields=['movie', 'show_date']),
        ]

class ShowSeatPricing(models.Model):
    """
    Model for seat category pricing for each show
    """
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='seat_pricing')
    seat_category = models.ForeignKey(SeatCategory, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.show} - {self.seat_category.name} - ₹{self.price}"
    
    class Meta:
        db_table = 'show_seat_pricing'
        unique_together = ('show', 'seat_category')