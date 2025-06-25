from rest_framework import serializers
from django.utils import timezone
from .models import Booking, BookedSeat, Payment, Coupon, CouponUsage

class BookedSeatSerializer(serializers.ModelSerializer):
    """
    Serializer for BookedSeat model
    """
    seat_number = serializers.CharField(source='seat.seat_number', read_only=True)
    row = serializers.CharField(source='seat.row', read_only=True)
    category_name = serializers.CharField(source='seat.category.name', read_only=True)
    
    class Meta:
        model = BookedSeat
        fields = ['seat_number', 'row', 'category_name', 'price']

class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model
    """
    class Meta:
        model = Payment
        fields = [
            'payment_id', 'payment_method', 'amount', 'status',
            'initiated_at', 'completed_at', 'failed_at'
        ]
        read_only_fields = ['payment_id', 'initiated_at', 'completed_at', 'failed_at']

class BookingListSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking list view
    """
    movie_title = serializers.ReadOnlyField()
    theater_name = serializers.ReadOnlyField()
    screen_name = serializers.ReadOnlyField()
    show_date = serializers.DateField(source='show.show_date', read_only=True)
    show_time = serializers.TimeField(source='show.show_time', read_only=True)
    movie_poster = serializers.ImageField(source='show.movie.poster', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'movie_title', 'theater_name', 'screen_name',
            'show_date', 'show_time', 'quantity', 'final_amount',
            'status', 'payment_status', 'booking_time', 'movie_poster'
        ]

class BookingDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking detail view
    """
    movie_title = serializers.ReadOnlyField()
    theater_name = serializers.ReadOnlyField()
    screen_name = serializers.ReadOnlyField()
    show_date = serializers.DateField(source='show.show_date', read_only=True)
    show_time = serializers.TimeField(source='show.show_time', read_only=True)
    movie_poster = serializers.ImageField(source='show.movie.poster', read_only=True)
    booked_seats = BookedSeatSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'movie_title', 'theater_name', 'screen_name',
            'show_date', 'show_time', 'quantity', 'total_amount',
            'convenience_fee', 'discount_amount', 'final_amount',
            'status', 'payment_status', 'phone_number', 'email',
            'booking_time', 'expiry_time', 'confirmed_at', 'cancelled_at',
            'movie_poster', 'booked_seats', 'payment', 'is_expired'
        ]

class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating bookings
    """
    seat_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text="List of seat IDs to book"
    )
    coupon_code = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'show', 'seat_ids', 'phone_number', 'email', 'coupon_code'
        ]
    
    def validate_seat_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one seat must be selected")
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 seats can be booked at once")
        return value
    
    def validate(self, data):
        show = data['show']
        seat_ids = data['seat_ids']
        
        # Check if show is active and not past
        if not show.is_active:
            raise serializers.ValidationError("Show is not active")
        
        if show.is_past:
            raise serializers.ValidationError("Cannot book tickets for past shows")
        
        # Check if seats exist and are available
        from theaters.models import Seat
        seats = Seat.objects.filter(id__in=seat_ids, screen=show.screen, is_active=True)
        
        if len(seats) != len(seat_ids):
            raise serializers.ValidationError("Some selected seats are not available")
        
        # Check if seats are already booked for this show
        booked_seat_ids = BookedSeat.objects.filter(
            booking__show=show,
            booking__status='confirmed',
            seat__id__in=seat_ids
        ).values_list('seat_id', flat=True)
        
        if booked_seat_ids:
            raise serializers.ValidationError("Some selected seats are already booked")
        
        data['seats'] = seats
        return data
    
    def create(self, validated_data):
        seat_ids = validated_data.pop('seat_ids')
        seats = validated_data.pop('seats')
        coupon_code = validated_data.pop('coupon_code', None)
        
        show = validated_data['show']
        user = self.context['request'].user
        
        # Calculate total amount
        total_amount = 0
        seat_prices = {}
        
        for seat in seats:
            # Get seat price from show pricing or use base price
            try:
                pricing = show.seat_pricing.get(seat_category=seat.category)
                price = pricing.price
            except:
                price = show.base_price
            
            seat_prices[seat.id] = price
            total_amount += price
        
        # Calculate convenience fee (₹20 per ticket)
        convenience_fee = len(seats) * 20
        
        # Apply coupon if provided
        discount_amount = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.can_be_used_by_user(user):
                    discount_amount = coupon.calculate_discount(total_amount)
            except Coupon.DoesNotExist:
                pass
        
        final_amount = total_amount + convenience_fee - discount_amount
        
        # Create booking
        booking = Booking.objects.create(
            user=user,
            show=show,
            quantity=len(seats),
            total_amount=total_amount,
            convenience_fee=convenience_fee,
            discount_amount=discount_amount,
            final_amount=final_amount,
            phone_number=validated_data['phone_number'],
            email=validated_data['email']
        )
        
        # Create booked seats
        for seat in seats:
            BookedSeat.objects.create(
                booking=booking,
                seat=seat,
                price=seat_prices[seat.id]
            )
        
        # Create coupon usage record if coupon was applied
        if coupon_code and discount_amount > 0:
            coupon = Coupon.objects.get(code=coupon_code)
            CouponUsage.objects.create(
                coupon=coupon,
                user=user,
                booking=booking,
                discount_amount=discount_amount
            )
            coupon.used_count += 1
            coupon.save()
        
        return booking

class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating payments
    """
    class Meta:
        model = Payment
        fields = ['booking', 'payment_method']
    
    def create(self, validated_data):
        booking = validated_data['booking']
        
        # Generate payment ID
        import uuid
        payment_id = f"PAY_{uuid.uuid4().hex[:12].upper()}"
        
        payment = Payment.objects.create(
            booking=booking,
            payment_id=payment_id,
            payment_method=validated_data['payment_method'],
            amount=booking.final_amount
        )
        
        return payment

class CouponSerializer(serializers.ModelSerializer):
    """
    Serializer for Coupon model
    """
    is_valid = serializers.ReadOnlyField()
    
    class Meta:
        model = Coupon
        fields = [
            'code', 'description', 'coupon_type', 'value',
            'minimum_amount', 'maximum_discount', 'valid_from',
            'valid_until', 'is_valid'
        ]

class CouponValidationSerializer(serializers.Serializer):
    """
    Serializer for coupon validation
    """
    coupon_code = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_coupon_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value)
            if not coupon.is_valid:
                raise serializers.ValidationError("Coupon is not valid or has expired")
            return value
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code")