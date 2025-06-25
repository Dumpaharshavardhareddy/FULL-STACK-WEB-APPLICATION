from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

class Booking(models.Model):
    """
    Model for movie ticket bookings
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # Booking details
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bookings')
    show = models.ForeignKey('theaters.Show', on_delete=models.CASCADE, related_name='bookings')
    
    # Booking information
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    convenience_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Contact information
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    
    # Timestamps
    booking_time = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField()
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.expiry_time:
            # Set expiry time to 15 minutes from booking time
            self.expiry_time = timezone.now() + timezone.timedelta(minutes=15)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.full_name}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expiry_time and self.status == 'pending'
    
    @property
    def movie_title(self):
        return self.show.movie.title
    
    @property
    def theater_name(self):
        return self.show.screen.theater.name
    
    @property
    def screen_name(self):
        return self.show.screen.name
    
    @property
    def show_datetime(self):
        return timezone.datetime.combine(self.show.show_date, self.show.show_time)
    
    def confirm_booking(self):
        """Confirm the booking"""
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save()
    
    def cancel_booking(self):
        """Cancel the booking"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.save()
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-booking_time']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['booking_id']),
            models.Index(fields=['show', 'status']),
        ]

class BookedSeat(models.Model):
    """
    Model for individual booked seats
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booked_seats')
    seat = models.ForeignKey('theaters.Seat', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.booking.booking_id} - {self.seat.seat_number}"
    
    class Meta:
        db_table = 'booked_seats'
        unique_together = ('booking', 'seat')

class Payment(models.Model):
    """
    Model for payment transactions
    """
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
        ('wallet', 'Digital Wallet'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    payment_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment gateway details
    gateway_transaction_id = models.CharField(max_length=200, blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='initiated')
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.booking.booking_id}"
    
    def mark_completed(self, transaction_id=None, response_data=None):
        """Mark payment as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if transaction_id:
            self.gateway_transaction_id = transaction_id
        if response_data:
            self.gateway_response = response_data
        self.save()
        
        # Update booking status
        self.booking.payment_status = 'completed'
        self.booking.confirm_booking()
    
    def mark_failed(self, response_data=None):
        """Mark payment as failed"""
        self.status = 'failed'
        self.failed_at = timezone.now()
        if response_data:
            self.gateway_response = response_data
        self.save()
        
        # Update booking status
        self.booking.payment_status = 'failed'
        self.booking.save()
    
    class Meta:
        db_table = 'payments'
        ordering = ['-initiated_at']

class Coupon(models.Model):
    """
    Model for discount coupons
    """
    COUPON_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPES)
    value = models.DecimalField(max_digits=8, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    user_limit = models.PositiveIntegerField(default=1)  # Per user limit
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.description}"
    
    @property
    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )
    
    def calculate_discount(self, amount):
        """Calculate discount amount for given amount"""
        if not self.is_valid or amount < self.minimum_amount:
            return 0
        
        if self.coupon_type == 'percentage':
            discount = (amount * self.value) / 100
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
        else:
            discount = self.value
        
        return min(discount, amount)
    
    def can_be_used_by_user(self, user):
        """Check if coupon can be used by the user"""
        if not self.is_valid:
            return False
        
        user_usage = CouponUsage.objects.filter(coupon=self, user=user).count()
        return user_usage < self.user_limit
    
    class Meta:
        db_table = 'coupons'
        ordering = ['-created_at']

class CouponUsage(models.Model):
    """
    Model to track coupon usage
    """
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.coupon.code} - {self.user.full_name}"
    
    class Meta:
        db_table = 'coupon_usages'
        unique_together = ('coupon', 'booking')
        ordering = ['-used_at']