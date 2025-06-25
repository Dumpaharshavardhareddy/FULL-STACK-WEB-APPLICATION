from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Booking, Payment, Coupon
from .serializers import (
    BookingListSerializer, BookingDetailSerializer, BookingCreateSerializer,
    PaymentCreateSerializer, PaymentSerializer, CouponSerializer,
    CouponValidationSerializer
)

class BookingListView(generics.ListAPIView):
    """
    API view for user's booking history
    """
    serializer_class = BookingListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-booking_time')

class BookingDetailView(generics.RetrieveAPIView):
    """
    API view for booking details
    """
    serializer_class = BookingDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'booking_id'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

class BookingCreateView(generics.CreateAPIView):
    """
    API view for creating bookings
    """
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        booking = serializer.save()
        # Send booking confirmation email
        self.send_booking_confirmation_email(booking)
        return booking
    
    def send_booking_confirmation_email(self, booking):
        """Send booking confirmation email to user"""
        try:
            subject = f'Booking Confirmation - {booking.movie_title}'
            
            # Prepare email context
            context = {
                'booking': booking,
                'user': booking.user,
                'movie': booking.show.movie,
                'theater': booking.show.screen.theater,
                'show': booking.show,
                'seats': booking.booked_seats.all(),
            }
            
            # Render email template
            html_message = render_to_string('emails/booking_confirmation.html', context)
            plain_message = render_to_string('emails/booking_confirmation.txt', context)
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.email],
                html_message=html_message,
                fail_silently=True
            )
        except Exception as e:
            # Log error but don't fail the booking
            print(f"Failed to send booking confirmation email: {e}")

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_booking(request, booking_id):
    """
    API view to cancel a booking
    """
    try:
        booking = Booking.objects.get(
            booking_id=booking_id,
            user=request.user
        )
    except Booking.DoesNotExist:
        return Response(
            {'error': 'Booking not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if booking can be cancelled
    if booking.status != 'confirmed':
        return Response(
            {'error': 'Only confirmed bookings can be cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if show is not past
    if booking.show.is_past:
        return Response(
            {'error': 'Cannot cancel booking for past shows'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check cancellation time (allow cancellation up to 2 hours before show)
    show_datetime = timezone.datetime.combine(booking.show.show_date, booking.show.show_time)
    show_datetime = timezone.make_aware(show_datetime)
    cancellation_deadline = show_datetime - timezone.timedelta(hours=2)
    
    if timezone.now() > cancellation_deadline:
        return Response(
            {'error': 'Booking cannot be cancelled within 2 hours of show time'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Cancel the booking
    with transaction.atomic():
        booking.cancel_booking()
        
        # Update payment status if payment was completed
        if hasattr(booking, 'payment') and booking.payment.status == 'completed':
            booking.payment.status = 'refunded'
            booking.payment.save()
            booking.payment_status = 'refunded'
            booking.save()
        
        # Send cancellation email
        send_cancellation_email(booking)
    
    return Response({
        'message': 'Booking cancelled successfully',
        'booking_id': booking.booking_id
    })

def send_cancellation_email(booking):
    """Send booking cancellation email"""
    try:
        subject = f'Booking Cancelled - {booking.movie_title}'
        
        context = {
            'booking': booking,
            'user': booking.user,
            'refund_amount': booking.final_amount if booking.payment_status == 'refunded' else 0,
        }
        
        html_message = render_to_string('emails/booking_cancellation.html', context)
        plain_message = render_to_string('emails/booking_cancellation.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            html_message=html_message,
            fail_silently=True
        )
    except Exception as e:
        print(f"Failed to send cancellation email: {e}")

class PaymentCreateView(generics.CreateAPIView):
    """
    API view for creating payments
    """
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        booking = serializer.validated_data['booking']
        
        # Check if user owns the booking
        if booking.user != request.user:
            return Response(
                {'error': 'You can only pay for your own bookings'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if booking is still valid
        if booking.is_expired:
            booking.status = 'expired'
            booking.save()
            return Response(
                {'error': 'Booking has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if payment already exists
        if hasattr(booking, 'payment'):
            return Response(
                {'error': 'Payment already initiated for this booking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment = serializer.save()
        
        # In a real application, you would integrate with payment gateway here
        # For demo purposes, we'll simulate payment processing
        
        return Response({
            'payment_id': payment.payment_id,
            'amount': payment.amount,
            'status': payment.status,
            'message': 'Payment initiated successfully'
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_payment(request, payment_id):
    """
    API view to process payment (mock implementation)
    """
    try:
        payment = Payment.objects.get(
            payment_id=payment_id,
            booking__user=request.user
        )
    except Payment.DoesNotExist:
        return Response(
            {'error': 'Payment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if payment.status != 'initiated':
        return Response(
            {'error': 'Payment cannot be processed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Mock payment processing
    # In real implementation, this would involve payment gateway integration
    payment_success = True  # Simulate successful payment
    
    if payment_success:
        with transaction.atomic():
            payment.mark_completed(
                transaction_id=f"TXN_{payment.payment_id}",
                response_data={'status': 'success', 'gateway': 'mock'}
            )
            
            # Send payment success email
            send_payment_success_email(payment.booking)
        
        return Response({
            'message': 'Payment completed successfully',
            'booking_id': payment.booking.booking_id,
            'payment_status': payment.status,
            'ticket_details': BookingDetailSerializer(
                payment.booking, 
                context={'request': request}
            ).data
        })
    else:
        payment.mark_failed(
            response_data={'status': 'failed', 'gateway': 'mock'}
        )
        
        return Response(
            {'error': 'Payment failed'},
            status=status.HTTP_400_BAD_REQUEST
        )

def send_payment_success_email(booking):
    """Send payment success and ticket details email"""
    try:
        subject = f'Payment Successful - Ticket Confirmed for {booking.movie_title}'
        
        context = {
            'booking': booking,
            'user': booking.user,
            'movie': booking.show.movie,
            'theater': booking.show.screen.theater,
            'show': booking.show,
            'seats': booking.booked_seats.all(),
            'payment': booking.payment,
        }
        
        html_message = render_to_string('emails/payment_success.html', context)
        plain_message = render_to_string('emails/payment_success.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            html_message=html_message,
            fail_silently=True
        )
    except Exception as e:
        print(f"Failed to send payment success email: {e}")

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_coupon(request):
    """
    API view to validate coupon code
    """
    serializer = CouponValidationSerializer(data=request.data)
    if serializer.is_valid():
        coupon_code = serializer.validated_data['coupon_code']
        amount = serializer.validated_data['amount']
        
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            
            if not coupon.can_be_used_by_user(request.user):
                return Response(
                    {'error': 'Coupon usage limit exceeded'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            discount_amount = coupon.calculate_discount(amount)
            
            return Response({
                'valid': True,
                'coupon': CouponSerializer(coupon).data,
                'discount_amount': discount_amount,
                'final_amount': amount - discount_amount
            })
            
        except Coupon.DoesNotExist:
            return Response(
                {'error': 'Invalid coupon code'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def booking_summary(request):
    """
    API view to get user's booking summary
    """
    user = request.user
    bookings = Booking.objects.filter(user=user)
    
    total_bookings = bookings.count()
    confirmed_bookings = bookings.filter(status='confirmed').count()
    cancelled_bookings = bookings.filter(status='cancelled').count()
    total_spent = bookings.filter(status='confirmed').aggregate(
        total=models.Sum('final_amount')
    )['total'] or 0
    
    # Recent bookings
    recent_bookings = bookings.order_by('-booking_time')[:5]
    
    return Response({
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_spent': total_spent,
        'recent_bookings': BookingListSerializer(
            recent_bookings, many=True, context={'request': request}
        ).data
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_ticket(request, booking_id):
    """
    API view to download ticket as PDF
    """
    try:
        booking = Booking.objects.get(
            booking_id=booking_id,
            user=request.user,
            status='confirmed'
        )
    except Booking.DoesNotExist:
        return Response(
            {'error': 'Booking not found or not confirmed'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # In a real implementation, you would generate a PDF ticket here
    # For now, we'll return the ticket data
    ticket_data = BookingDetailSerializer(booking, context={'request': request}).data
    
    return Response({
        'message': 'Ticket download initiated',
        'ticket_data': ticket_data,
        'download_url': f'/api/bookings/{booking_id}/ticket.pdf'  # Mock URL
    })

# Admin views
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_booking_stats(request):
    """
    API view for admin booking statistics
    """
    from django.db.models import Sum, Count
    from django.utils import timezone
    
    today = timezone.now().date()
    
    # Today's stats
    today_bookings = Booking.objects.filter(booking_time__date=today)
    today_revenue = today_bookings.filter(status='confirmed').aggregate(
        total=Sum('final_amount')
    )['total'] or 0
    
    # Overall stats
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(status='confirmed').aggregate(
        total=Sum('final_amount')
    )['total'] or 0
    
    # Popular movies
    popular_movies = Booking.objects.filter(status='confirmed').values(
        'show__movie__title'
    ).annotate(
        booking_count=Count('id'),
        revenue=Sum('final_amount')
    ).order_by('-booking_count')[:10]
    
    return Response({
        'today_bookings': today_bookings.count(),
        'today_revenue': today_revenue,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'popular_movies': popular_movies
    })