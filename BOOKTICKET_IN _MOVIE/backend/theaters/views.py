from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from .models import Theater, Screen, Show, Seat, SeatCategory
from .serializers import (
    TheaterListSerializer, TheaterDetailSerializer, ScreenSerializer,
    ShowListSerializer, ShowDetailSerializer, ShowCreateSerializer,
    SeatSerializer, SeatCategorySerializer
)

class TheaterListView(generics.ListAPIView):
    """
    API view for listing theaters
    """
    queryset = Theater.objects.filter(is_active=True)
    serializer_class = TheaterListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['city', 'state']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by city
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset

class TheaterDetailView(generics.RetrieveAPIView):
    """
    API view for theater details
    """
    queryset = Theater.objects.filter(is_active=True)
    serializer_class = TheaterDetailSerializer
    permission_classes = [permissions.AllowAny]

class ShowListView(generics.ListAPIView):
    """
    API view for listing shows
    """
    queryset = Show.objects.filter(is_active=True)
    serializer_class = ShowListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['movie', 'screen__theater', 'show_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by movie
        movie_id = self.request.query_params.get('movie')
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        
        # Filter by theater
        theater_id = self.request.query_params.get('theater')
        if theater_id:
            queryset = queryset.filter(screen__theater_id=theater_id)
        
        # Filter by city
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(screen__theater__city__icontains=city)
        
        # Filter by date
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(show_date=date)
        else:
            # Default to today and future shows
            today = timezone.now().date()
            queryset = queryset.filter(show_date__gte=today)
        
        return queryset.order_by('show_date', 'show_time')

class ShowDetailView(generics.RetrieveAPIView):
    """
    API view for show details
    """
    queryset = Show.objects.filter(is_active=True)
    serializer_class = ShowDetailSerializer
    permission_classes = [permissions.AllowAny]

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def shows_by_movie_and_city(request, movie_id):
    """
    API view to get shows for a movie in a specific city
    """
    city = request.query_params.get('city', '')
    date = request.query_params.get('date', timezone.now().date())
    
    shows = Show.objects.filter(
        movie_id=movie_id,
        is_active=True,
        show_date=date
    )
    
    if city:
        shows = shows.filter(screen__theater__city__icontains=city)
    
    # Group shows by theater
    theaters_data = {}
    for show in shows:
        theater_id = show.screen.theater.id
        theater_name = show.screen.theater.name
        
        if theater_id not in theaters_data:
            theaters_data[theater_id] = {
                'id': theater_id,
                'name': theater_name,
                'address': show.screen.theater.full_address,
                'facilities': show.screen.theater.facilities,
                'shows': []
            }
        
        theaters_data[theater_id]['shows'].append({
            'id': show.id,
            'screen_name': show.screen.name,
            'screen_type': show.screen.screen_type,
            'show_time': show.show_time,
            'base_price': show.base_price,
            'available_seats': show.available_seats,
            'is_housefull': show.is_housefull
        })
    
    return Response(list(theaters_data.values()))

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def seat_layout(request, show_id):
    """
    API view to get seat layout for a show
    """
    try:
        show = Show.objects.get(id=show_id, is_active=True)
    except Show.DoesNotExist:
        return Response({'error': 'Show not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get all seats for the screen
    seats = show.screen.seats.filter(is_active=True).order_by('row', 'column')
    
    # Get booked seats for this show
    from bookings.models import BookedSeat
    booked_seats = BookedSeat.objects.filter(
        booking__show=show,
        booking__status='confirmed'
    ).values_list('seat__seat_number', flat=True)
    
    # Get seat pricing for this show
    seat_pricing = {
        pricing.seat_category.id: pricing.price 
        for pricing in show.seat_pricing.all()
    }
    
    # Organize seats by row
    seat_layout = {}
    for seat in seats:
        if seat.row not in seat_layout:
            seat_layout[seat.row] = []
        
        seat_data = {
            'id': seat.id,
            'seat_number': seat.seat_number,
            'column': seat.column,
            'category': {
                'id': seat.category.id,
                'name': seat.category.name,
                'color_code': seat.category.color_code
            },
            'price': seat_pricing.get(seat.category.id, show.base_price),
            'is_booked': seat.seat_number in booked_seats,
            'is_accessible': seat.is_accessible
        }
        seat_layout[seat.row].append(seat_data)
    
    return Response({
        'show': ShowDetailSerializer(show, context={'request': request}).data,
        'seat_layout': seat_layout,
        'seat_categories': SeatCategorySerializer(SeatCategory.objects.all(), many=True).data
    })

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def cities_list(request):
    """
    API view to get all cities with theaters
    """
    cities = Theater.objects.filter(is_active=True).values_list('city', flat=True).distinct().order_by('city')
    return Response(list(cities))

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def theaters_by_city(request, city):
    """
    API view to get theaters in a specific city
    """
    theaters = Theater.objects.filter(is_active=True, city__icontains=city)
    serializer = TheaterListSerializer(theaters, many=True, context={'request': request})
    return Response(serializer.data)

# Admin views for theater management
class ShowCreateView(generics.CreateAPIView):
    """
    API view for creating shows (Admin only)
    """
    queryset = Show.objects.all()
    serializer_class = ShowCreateSerializer
    permission_classes = [permissions.IsAdminUser]

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def bulk_create_shows(request):
    """
    API view for bulk creating shows
    """
    shows_data = request.data.get('shows', [])
    created_shows = []
    errors = []
    
    for show_data in shows_data:
        serializer = ShowCreateSerializer(data=show_data)
        if serializer.is_valid():
            show = serializer.save()
            created_shows.append(show.id)
        else:
            errors.append({
                'data': show_data,
                'errors': serializer.errors
            })
    
    return Response({
        'created_shows': created_shows,
        'errors': errors,
        'total_created': len(created_shows),
        'total_errors': len(errors)
    })