from rest_framework import serializers
from .models import Movie, Genre, Language, MovieReview, MovieImage

class GenreSerializer(serializers.ModelSerializer):
    """
    Serializer for Genre model
    """
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description']

class LanguageSerializer(serializers.ModelSerializer):
    """
    Serializer for Language model
    """
    class Meta:
        model = Language
        fields = ['id', 'name', 'code']

class MovieImageSerializer(serializers.ModelSerializer):
    """
    Serializer for MovieImage model
    """
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MovieImage
        fields = ['id', 'image', 'image_url', 'caption', 'is_featured']
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

class MovieReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for MovieReview model
    """
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = MovieReview
        fields = ['id', 'rating', 'review', 'user_name', 'is_verified', 'created_at']
        read_only_fields = ['user', 'is_verified']

class MovieListSerializer(serializers.ModelSerializer):
    """
    Serializer for Movie list view
    """
    genres = GenreSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    poster_url = serializers.SerializerMethodField()
    duration_formatted = serializers.ReadOnlyField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'slug', 'description', 'duration', 'duration_formatted',
            'release_date', 'director', 'rating', 'certificate', 'poster', 'poster_url',
            'genres', 'languages', 'is_featured', 'trailer_url'
        ]
    
    def get_poster_url(self, obj):
        if obj.poster:
            return self.context['request'].build_absolute_uri(obj.poster.url)
        return None

class MovieDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Movie detail view
    """
    genres = GenreSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    cast_list = serializers.ReadOnlyField()
    duration_formatted = serializers.ReadOnlyField()
    poster_url = serializers.SerializerMethodField()
    images = MovieImageSerializer(many=True, read_only=True)
    reviews = MovieReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'slug', 'description', 'duration', 'duration_formatted',
            'release_date', 'end_date', 'director', 'cast', 'cast_list', 'rating',
            'certificate', 'poster', 'poster_url', 'trailer_url', 'genres', 'languages',
            'images', 'reviews', 'average_rating', 'total_reviews', 'is_featured'
        ]
    
    def get_poster_url(self, obj):
        if obj.poster:
            return self.context['request'].build_absolute_uri(obj.poster.url)
        return None
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(is_verified=True)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0.0
    
    def get_total_reviews(self, obj):
        return obj.reviews.filter(is_verified=True).count()

class MovieReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating movie reviews
    """
    class Meta:
        model = MovieReview
        fields = ['movie', 'rating', 'review']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)