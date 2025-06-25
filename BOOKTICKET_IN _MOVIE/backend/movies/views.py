from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from .models import Movie, Genre, Language, MovieReview
from .serializers import (
    MovieListSerializer, MovieDetailSerializer, GenreSerializer,
    LanguageSerializer, MovieReviewSerializer, MovieReviewCreateSerializer
)

class MovieListView(generics.ListAPIView):
    """
    API view for listing movies with filtering and search
    """
    queryset = Movie.objects.filter(is_active=True)
    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genres__name', 'languages__name', 'certificate', 'is_featured']
    search_fields = ['title', 'director', 'cast', 'description']
    ordering_fields = ['release_date', 'rating', 'title']
    ordering = ['-release_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by location (city)
        city = self.request.query_params.get('city')
        if city:
            # Filter movies that have shows in theaters in the specified city
            queryset = queryset.filter(
                shows__theater__city__icontains=city
            ).distinct()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(release_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(release_date__lte=end_date)
        
        return queryset

class MovieDetailView(generics.RetrieveAPIView):
    """
    API view for movie details
    """
    queryset = Movie.objects.filter(is_active=True)
    serializer_class = MovieDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

class FeaturedMoviesView(generics.ListAPIView):
    """
    API view for featured movies
    """
    queryset = Movie.objects.filter(is_active=True, is_featured=True)
    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]

class NowShowingMoviesView(generics.ListAPIView):
    """
    API view for currently showing movies
    """
    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        from django.utils import timezone
        today = timezone.now().date()
        return Movie.objects.filter(
            is_active=True,
            release_date__lte=today,
            shows__show_date=today
        ).distinct()

class UpcomingMoviesView(generics.ListAPIView):
    """
    API view for upcoming movies
    """
    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        from django.utils import timezone
        today = timezone.now().date()
        return Movie.objects.filter(
            is_active=True,
            release_date__gt=today
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def genres_list(request):
    """
    API view to get all genres
    """
    genres = Genre.objects.all()
    serializer = GenreSerializer(genres, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def languages_list(request):
    """
    API view to get all languages
    """
    languages = Language.objects.all()
    serializer = LanguageSerializer(languages, many=True)
    return Response(serializer.data)

class MovieReviewListView(generics.ListAPIView):
    """
    API view for movie reviews
    """
    serializer_class = MovieReviewSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        movie_id = self.kwargs['movie_id']
        return MovieReview.objects.filter(
            movie_id=movie_id,
            is_verified=True
        ).order_by('-created_at')

class MovieReviewCreateView(generics.CreateAPIView):
    """
    API view for creating movie reviews
    """
    serializer_class = MovieReviewCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['GET'])
@permission_classes([AllowAny])
def movie_search(request):
    """
    API view for advanced movie search
    """
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    genre = request.GET.get('genre', '')
    language = request.GET.get('language', '')
    
    movies = Movie.objects.filter(is_active=True)
    
    if query:
        movies = movies.filter(
            Q(title__icontains=query) |
            Q(director__icontains=query) |
            Q(cast__icontains=query) |
            Q(description__icontains=query)
        )
    
    if city:
        movies = movies.filter(shows__theater__city__icontains=city).distinct()
    
    if genre:
        movies = movies.filter(genres__name__icontains=genre)
    
    if language:
        movies = movies.filter(languages__name__icontains=language)
    
    serializer = MovieListSerializer(movies, many=True, context={'request': request})
    return Response({
        'movies': serializer.data,
        'total': movies.count()
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def movie_by_theater(request, theater_id):
    """
    API view to get movies showing in a specific theater
    """
    from django.utils import timezone
    today = timezone.now().date()
    
    movies = Movie.objects.filter(
        is_active=True,
        shows__theater_id=theater_id,
        shows__show_date__gte=today
    ).distinct()
    
    serializer = MovieListSerializer(movies, many=True, context={'request': request})
    return Response(serializer.data)