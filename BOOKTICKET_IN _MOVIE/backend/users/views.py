from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileSerializer, PasswordChangeSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    API view for user login
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    API view for user logout
    """
    try:
        request.user.auth_token.delete()
    except:
        pass
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for user profile management
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_bookings(request):
    """
    API view to get user's booking history
    """
    from bookings.models import Booking
    from bookings.serializers import BookingSerializer
    
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    serializer = BookingSerializer(bookings, many=True, context={'request': request})
    
    return Response({
        'bookings': serializer.data,
        'total_bookings': bookings.count()
    }, status=status.HTTP_200_OK)

class PasswordChangeView(generics.UpdateAPIView):
    """
    API view for changing user password
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.get_object()
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_preferences(request):
    """
    API view to get user preferences
    """
    profile = request.user.profile
    preferred_theaters = profile.preferred_theaters.all()
    
    from theaters.serializers import TheaterSerializer
    
    return Response({
        'preferred_language': profile.preferred_language,
        'preferred_theaters': TheaterSerializer(preferred_theaters, many=True, context={'request': request}).data,
        'notification_preferences': profile.notification_preferences
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_preferences(request):
    """
    API view to update user preferences
    """
    profile = request.user.profile
    
    if 'preferred_language' in request.data:
        profile.preferred_language = request.data['preferred_language']
    
    if 'notification_preferences' in request.data:
        profile.notification_preferences = request.data['notification_preferences']
    
    if 'preferred_theaters' in request.data:
        from theaters.models import Theater
        theater_ids = request.data['preferred_theaters']
        theaters = Theater.objects.filter(id__in=theater_ids)
        profile.preferred_theaters.set(theaters)
    
    profile.save()
    
    return Response({'message': 'Preferences updated successfully'}, status=status.HTTP_200_OK)