from rest_framework import serializers
from .models import Theater, Screen, Show, Seat, SeatCategory, ShowSeatPricing

class SeatCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for SeatCategory model
    """
    class Meta:
        model = SeatCategory
        fields = ['id', 'name', 'description', 'color_code']

class SeatSerializer(serializers.ModelSerializer):
    """
    Serializer for Seat model
    """
    category = SeatCategorySerializer(read_only=True)
    
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'row', 'column', 'category', 'is_active', 'is_accessible']

class ScreenSerializer(serializers.ModelSerializer):
    """
    Serializer for Screen model
    """
    seats = SeatSerializer(many=True, read_only=True)
    
    class Meta:
        model = Screen
        fields = ['id', 'name', 'screen_type', 'total_seats', 'rows', 'seats_per_row', 'seats']

class TheaterListSerializer(serializers.ModelSerializer):
    """
    Serializer for Theater list view
    """
    screen_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Theater
        fields = [
            'id', 'name', 'address', 'city', 'state', 'pincode',
            'phone', 'email', 'total_screens', 'screen_count', 'facilities'
        ]
    
    def get_screen_count(self, obj):
        return obj.screens.filter(is_active=True).count()

class TheaterDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Theater detail view
    """
    screens = ScreenSerializer(many=True, read_only=True)
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = Theater
        fields = [
            'id', 'name', 'address', 'full_address', 'city', 'state', 'pincode',
            'phone', 'email', 'total_screens', 'facilities', 'latitude', 'longitude',
            'screens'
        ]

class ShowSeatPricingSerializer(serializers.ModelSerializer):
    """
    Serializer for ShowSeatPricing model
    """
    seat_category = SeatCategorySerializer(read_only=True)
    
    class Meta:
        model = ShowSeatPricing
        fields = ['seat_category', 'price']

class ShowListSerializer(serializers.ModelSerializer):
    """
    Serializer for Show list view
    """
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    movie_poster = serializers.ImageField(source='movie.poster', read_only=True)
    theater_name = serializers.CharField(source='screen.theater.name', read_only=True)
    screen_name = serializers.CharField(source='screen.name', read_only=True)
    screen_type = serializers.CharField(source='screen.screen_type', read_only=True)
    available_seats = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    
    class Meta:
        model = Show
        fields = [
            'id', 'movie_title', 'movie_poster', 'theater_name', 'screen_name',
            'screen_type', 'show_date', 'show_time', 'base_price', 'available_seats',
            'is_housefull', 'is_past'
        ]

class ShowDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Show detail view
    """
    movie = serializers.StringRelatedField()
    screen = ScreenSerializer(read_only=True)
    seat_pricing = ShowSeatPricingSerializer(many=True, read_only=True)
    available_seats = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    theater_name = serializers.CharField(source='screen.theater.name', read_only=True)
    
    class Meta:
        model = Show
        fields = [
            'id', 'movie', 'screen', 'theater_name', 'show_date', 'show_time',
            'base_price', 'seat_pricing', 'available_seats', 'is_housefull', 'is_past'
        ]

class ShowCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating shows
    """
    class Meta:
        model = Show
        fields = ['movie', 'screen', 'show_date', 'show_time', 'base_price']
        
    def validate(self, data):
        # Check if show time is in the future
        from django.utils import timezone
        show_datetime = timezone.datetime.combine(data['show_date'], data['show_time'])
        if timezone.make_aware(show_datetime) <= timezone.now():
            raise serializers.ValidationError("Show time must be in the future")
        
        # Check if screen is available at the given time
        existing_show = Show.objects.filter(
            screen=data['screen'],
            show_date=data['show_date'],
            show_time=data['show_time']
        ).exists()
        
        if existing_show:
            raise serializers.ValidationError("Screen is already booked for this time slot")
        
        return data