from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Count
from product.serializers import AnalyticsEventSerializer
from product.models import AnalyticsEvent, Product
@api_view(['GET'])
@permission_classes([AllowAny])
def affiliate_redirect(request, product_id):
    """
    Redirect user to affiliate link and track the click event
    URL: /api/affiliate/redirect/<product_id>/
    """
    try:
        product = Product.objects.get(id=product_id)
        
        if not product.affiliate_url:
            return Response(
                {'detail': 'This product does not have an affiliate link'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Track analytics event
        track_event(
            request=request,
            event_type='store_click',
            product=product,
            metadata={
                'store': product.store,
                'category': product.category,
                'tag': product.tag,
                'price': str(product.price)
            }
        )
        
        # Redirect to affiliate URL
        return redirect(product.affiliate_url)
        
    except ObjectDoesNotExist:
        return Response(
            {'detail': f'Product with id {product_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def track_analytics_event(request):
    """
    Track analytics events from frontend
    URL: /api/analytics/track/
    
    Body:
    {
        "event_type": "store_click",
        "product_id": 123,
        "metadata": {...}
    }
    """
    event_type = request.data.get('event_type')
    product_id = request.data.get('product_id')
    metadata = request.data.get('metadata', {})
    
    valid_events = [
        'store_click', 'list_create', 'list_reorder',
        'savings_add', 'paywall_view', 'subscribe_success'
    ]
    
    if event_type not in valid_events:
        return Response(
            {'detail': f'Invalid event type. Must be one of: {", ".join(valid_events)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    product = None
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            pass
    
    track_event(
        request=request,
        event_type=event_type,
        product=product,
        metadata=metadata
    )
    
    return Response({'detail': 'Event tracked successfully'}, status=status.HTTP_200_OK)


def track_event(request, event_type, product=None, metadata=None):
    """
    Helper function to track analytics events
    This can be integrated with Google Analytics, Mixpanel, etc.
    """
    # Get user info
    user = request.user if request.user.is_authenticated else None
    
    # Get IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    # Get user agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Create event record (if using AnalyticsEvent model)
    """
    AnalyticsEvent.objects.create(
        user=user,
        event_type=event_type,
        product=product,
        metadata=metadata or {},
        ip_address=ip_address,
        user_agent=user_agent
    )
    """
    
    # For now, just log it
    print(f"[ANALYTICS] {event_type} - User: {user}, Product: {product}, Metadata: {metadata}")
    
    # TODO: Send to Google Analytics
    # Example using GA4 Measurement Protocol:
    """
    import requests
    
    ga_measurement_id = 'G-XXXXXXXXXX'
    ga_api_secret = 'your_api_secret'
    
    payload = {
        'client_id': str(user.id) if user else ip_address,
        'events': [{
            'name': event_type,
            'params': {
                'product_id': product.id if product else None,
                'product_name': product.name if product else None,
                'store': product.store if product else None,
                **(metadata or {})
            }
        }]
    }
    
    requests.post(
        f'https://www.google-analytics.com/mp/collect?measurement_id={ga_measurement_id}&api_secret={ga_api_secret}',
        json=payload
    )
    """


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics_summary(request):
    events = AnalyticsEvent.objects.filter(user=request.user)
    summary = events.values('event_type').annotate(count=Count('event_type'))
    recent_events = AnalyticsEventSerializer(events[:10], many=True).data
    return Response({
        'total_events': events.count(),
        'events_by_type': list(summary),
        'recent_events': recent_events
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_purchase(request, product_id):
    """
    Track when a user makes a purchase through affiliate link
    This should be called after successful purchase confirmation
    URL: /api/affiliate/purchase/<product_id>/
    
    Body:
    {
        "regular_price": 100.00,
        "affiliate_price": 85.00,
        "order_id": "ORDER123"
    }
    """
    try:
        product = Product.objects.get(id=product_id)
    except ObjectDoesNotExist:
        return Response(
            {'detail': f'Product with id {product_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    regular_price = float(request.data.get('regular_price', 0))
    affiliate_price = float(request.data.get('affiliate_price', 0))
    order_id = request.data.get('order_id')
    
    if affiliate_price > regular_price:
        return Response(
            {'detail': 'Affiliate price cannot be greater than regular price'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create savings entry
    from product.models import SavingsEntry
    savings_entry = SavingsEntry.objects.create(
        created_by=request.user,
        product=product,
        regular_price=regular_price,
        affiliate_price=affiliate_price,
        savings=regular_price - affiliate_price
    )
    
    # Track analytics
    track_event(
        request=request,
        event_type='savings_add',
        product=product,
        metadata={
            'order_id': order_id,
            'savings': str(savings_entry.savings),
            'regular_price': str(regular_price),
            'affiliate_price': str(affiliate_price)
        }
    )
    
    return Response({
        'detail': 'Purchase tracked successfully',
        'savings_id': savings_entry.id,
        'savings_amount': float(savings_entry.savings)
    }, status=status.HTTP_201_CREATED)