import json
import random
import string
import logging
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Value, Prefetch
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.html import strip_tags

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

import requests

from accounts.models import (
    Customer, Country, DestinationRegion, SiteSetting, TourSupplier,
    Category, Slider, Newsletter, ContactUs, CustomerReviewStatic,
    Page, City, Tour, TourImage, TourHighlight, TourIncluded, TourExcluded,
    TourItinerary, TourRequirement, TourFAQ, TourPricing, TourSchedule,
    TourTimeSlot, TimeSlot, TourReview, Booking, BookingParticipant,
    Coupon, CouponUsage, BlogPost, TeamMember, FeatureSection, FeatureSectionTour,
    WebsiteMenu, FAQ, Souvenir, SouvenirOrder, SouvenirOrderItem,
    SouvenirPickuplocation, Bike, BikeAddon, BikeAddonPrice,
    BikeBooking, BikeBookingAddon, Wishlist
)

from .serializers import (
    SiteSettingSerializer, WebsiteMenuSerializer, SliderSerializer,
    FAQSerializer, CustomerReviewStaticSerializer, PageListSerializer,
    PageDetailSerializer, TeamMemberSerializer, CountrySerializer,
    CitySerializer, DestinationRegionSerializer, CategorySerializer,
    TourSupplierSerializer, TourListSerializer, TourDetailSerializer,
    TourReviewSerializer, TourReviewCreateSerializer, FeatureSectionSerializer,
    CouponSerializer, BookingSerializer, BookingCreateSerializer,
    BlogPostListSerializer, BlogPostDetailSerializer, SouvenirSerializer,
    SouvenirPickuplocationSerializer, SouvenirOrderSerializer,
    SouvenirOrderCreateSerializer, BikeSerializer, BikeBookingSerializer,
    BikeBookingCreateSerializer, ContactUsSerializer, NewsletterSerializer,
    CustomerUserSerializer, CustomerRegisterSerializer,
    CustomerLoginSerializer, CustomerProfileUpdateSerializer, WishlistSerializer
)

logger = logging.getLogger(__name__)


def parse_id_from_param(param):
    """Handles both raw IDs (12) and slug-id strings ('my-tour-title-12')"""
    if isinstance(param, int):
        return param
    if isinstance(param, str):
        parts = param.strip().split('-')
        last_part = parts[-1]
        if last_part.isdigit():
            return int(last_part)
    return None


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


# ==============================================================================
# 1. SITE CONFIGURATION & NAVIGATION
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def site_config(request):
    """
    Returns global site settings, navigation menus, languages, and site meta.
    Ideal for Next.js layout, header, footer, and metadata initialization.
    """
    setting = SiteSetting.get_settings()
    settings_data = SiteSettingSerializer(setting, context={'request': request}).data if setting else {}
    
    menus = WebsiteMenu.objects.filter(status='active').order_by('rank')
    menus_data = WebsiteMenuSerializer(menus, many=True, context={'request': request}).data
    
    return Response({
        'settings': settings_data,
        'menus': menus_data,
        'languages': [
            {'code': 'en', 'name': 'English'},
            {'code': 'dk', 'name': 'Danish'},
        ],
        'currency': {
            'code': 'USD',
            'symbol': '$',
        }
    })


# ==============================================================================
# 2. HOMEPAGE AGGREGATOR
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def home_page_data(request):
    """
    Consolidated payload for the Next.js home page (sliders, tours, categories, reviews, blogs, faqs).
    Enables single-request Next.js SSR / ISR hydration.
    """
    sliders = Slider.objects.filter(status='active').order_by('display_order', '-created_at')
    
    categories = Category.objects.filter(status='active').annotate(
        tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('display_order', 'name')
    
    destinations = DestinationRegion.objects.filter(is_active=True).annotate(
        tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('name')[:8]
    
    cities = City.objects.filter(is_active=True).annotate(
        tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('name')[:8]
    
    featured_tours = Tour.objects.filter(status='active', is_featured=True).annotate(
        calculated_average_rating=Coalesce(Avg('reviews__overall_rating'), Value(0.0)),
        calculated_total_reviews=Count('reviews')
    ).select_related('supplier', 'category', 'destination_region', 'city', 'city__country').prefetch_related('images').order_by('rank')[:8]

    popular_tours = Tour.objects.filter(status='active', is_bestseller=True).annotate(
        calculated_average_rating=Coalesce(Avg('reviews__overall_rating'), Value(0.0)),
        calculated_total_reviews=Count('reviews')
    ).select_related('supplier', 'category', 'destination_region', 'city', 'city__country').prefetch_related('images').order_by('rank')[:8]

    all_tours = Tour.objects.filter(status='active').annotate(
        calculated_average_rating=Coalesce(Avg('reviews__overall_rating'), Value(0.0)),
        calculated_total_reviews=Count('reviews')
    ).select_related('supplier', 'category', 'destination_region', 'city', 'city__country').prefetch_related('images').order_by('rank')[:12]

    feature_sections = FeatureSection.objects.filter(status='active').prefetch_related(
        Prefetch('section_tours__tour', queryset=Tour.objects.filter(status='active').annotate(
            calculated_average_rating=Coalesce(Avg('reviews__overall_rating'), Value(0.0)),
            calculated_total_reviews=Count('reviews')
        ).select_related('supplier', 'category', 'city', 'destination_region').prefetch_related('images'))
    ).order_by('rank', '-created_at')[:4]

    reviews = CustomerReviewStatic.objects.filter(is_active=True).order_by('display_order', '-created_at')[:10]
    featured_blogs = BlogPost.objects.filter(status='published', is_featured=True).order_by('-created_at')[:3]
    faqs = FAQ.objects.filter(status='active', is_featured=True).order_by('display_order', '-created_at')[:6]
    souvenirs = Souvenir.objects.filter(status='active').order_by('-created_at')[:8]
    team_members = TeamMember.objects.all().order_by('-created_at')[:6]

    serializer_context = {'request': request}

    return Response({
        'sliders': SliderSerializer(sliders, many=True, context=serializer_context).data,
        'categories': CategorySerializer(categories, many=True, context=serializer_context).data,
        'destinations': DestinationRegionSerializer(destinations, many=True, context=serializer_context).data,
        'cities': CitySerializer(cities, many=True, context=serializer_context).data,
        'featured_tours': TourListSerializer(featured_tours, many=True, context=serializer_context).data,
        'popular_tours': TourListSerializer(popular_tours, many=True, context=serializer_context).data,
        'all_tours': TourListSerializer(all_tours, many=True, context=serializer_context).data,
        'feature_sections': FeatureSectionSerializer(feature_sections, many=True, context=serializer_context).data,
        'customer_reviews': CustomerReviewStaticSerializer(reviews, many=True, context=serializer_context).data,
        'featured_blogs': BlogPostListSerializer(featured_blogs, many=True, context=serializer_context).data,
        'faqs': FAQSerializer(faqs, many=True, context=serializer_context).data,
        'souvenirs': SouvenirSerializer(souvenirs, many=True, context=serializer_context).data,
        'team_members': TeamMemberSerializer(team_members, many=True, context=serializer_context).data,
    })


# ==============================================================================
# 3. TOURS API
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def tour_list(request):
    """
    Search and filter tours.
    Supports query params: search/q, category, country, region, city, supplier,
    min_price, max_price, rating, difficulty, start_date, sort,
    features (live_guide, skip_the_line, instant_confirmation, wheelchair_accessible, mobile_ticket, free_cancellation).
    """
    search_query = request.GET.get('search') or request.GET.get('q', '').strip()
    category_param = request.GET.get('category')
    supplier_param = request.GET.get('supplier')
    country_param = request.GET.get('country')
    region_param = request.GET.get('region')
    city_param = request.GET.get('city')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    rating = request.GET.get('rating')
    difficulty = request.GET.get('difficulty')
    sort_by = request.GET.get('sort', 'recommended')

    tours = Tour.objects.filter(status='active').annotate(
        calculated_average_rating=Coalesce(Avg('reviews__overall_rating'), Value(0.0)),
        calculated_total_reviews=Count('reviews')
    ).select_related(
        'supplier', 'category', 'destination_region', 'city', 'city__country'
    ).prefetch_related('images')

    if search_query:
        tours = tours.filter(
            Q(title__icontains=search_query) |
            Q(title_dk__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(destination_region__name__icontains=search_query)
        )

    if category_param:
        cat_id = parse_id_from_param(category_param)
        if cat_id:
            tours = tours.filter(category_id=cat_id)
        else:
            tours = tours.filter(category__slug=category_param)

    if country_param:
        cnt_id = parse_id_from_param(country_param)
        if cnt_id:
            tours = tours.filter(city__country_id=cnt_id)
        else:
            tours = tours.filter(city__country__code__iexact=country_param)

    if region_param:
        reg_id = parse_id_from_param(region_param)
        if reg_id:
            tours = tours.filter(destination_region_id=reg_id)
        else:
            tours = tours.filter(destination_region__slug=region_param)

    if city_param:
        ct_id = parse_id_from_param(city_param)
        if ct_id:
            tours = tours.filter(city_id=ct_id)
        else:
            tours = tours.filter(city__slug=city_param)

    if supplier_param:
        tours = tours.filter(supplier_id=supplier_param)

    if min_price:
        try:
            tours = tours.filter(base_price__gte=Decimal(min_price))
        except Exception:
            pass

    if max_price:
        try:
            tours = tours.filter(base_price__lte=Decimal(max_price))
        except Exception:
            pass

    if rating:
        try:
            tours = tours.filter(calculated_average_rating__gte=float(rating))
        except Exception:
            pass

    if difficulty:
        tours = tours.filter(difficulty_level__iexact=difficulty)

    # Boolean feature filters
    feature_keys = [
        'live_guide', 'skip_the_line', 'instant_confirmation',
        'wheelchair_accessible', 'mobile_ticket', 'free_cancellation'
    ]
    for key in feature_keys:
        val = request.GET.get(key)
        if val in ('true', '1', 'yes'):
            tours = tours.filter(**{key: True})

    # Sorting
    if sort_by == 'price_low' or sort_by == 'price_asc':
        tours = tours.order_by('base_price')
    elif sort_by == 'price_high' or sort_by == 'price_desc':
        tours = tours.order_by('-base_price')
    elif sort_by == 'rating':
        tours = tours.order_by('-calculated_average_rating', '-calculated_total_reviews')
    elif sort_by == 'newest':
        tours = tours.order_by('-created_at')
    elif sort_by == 'popular':
        tours = tours.order_by('-total_bookings', '-calculated_total_reviews')
    else:  # recommended
        tours = tours.order_by('rank', '-created_at')

    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(tours, request)
    serializer = TourListSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def tour_detail(request, tour_id):
    """
    Get full details for a tour by integer ID, slug-ID, or slug.
    Includes highlights, inclusions, exclusions, itinerary, requirements, faqs,
    pricing options, timeslots, reviews, and related tours.
    """
    tour = None
    target_id = parse_id_from_param(tour_id)
    if target_id:
        tour = Tour.objects.filter(pk=target_id, status='active').first()
    
    if not tour:
        tour = Tour.objects.filter(slug=tour_id, status='active').first()

    if not tour:
        return Response({'detail': 'Tour not found.'}, status=status.HTTP_404_NOT_FOUND)

    tour = Tour.objects.annotate(
        calculated_average_rating=Coalesce(Avg('reviews__overall_rating'), Value(0.0)),
        calculated_total_reviews=Count('reviews')
    ).select_related(
        'supplier', 'category', 'destination_region', 'city', 'city__country'
    ).prefetch_related(
        'images', 'highlights', 'included_items', 'excluded_items',
        'itinerary_steps', 'requirements', 'faqs', 'pricing_options',
        'tour_timeslots__time_slot'
    ).get(pk=tour.pk)

    serializer = TourDetailSerializer(tour, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_tour_review(request, tour_id):
    """Submit a review for a tour."""
    target_id = parse_id_from_param(tour_id)
    tour = get_object_or_404(Tour, pk=target_id or tour_id, status='active')
    
    serializer = TourReviewCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    customer, _ = Customer.objects.get_or_create(user=request.user)
    
    verified_booking = Booking.objects.filter(
        customer=customer,
        tour=tour,
        status='completed'
    ).first()

    review = serializer.save(
        tour=tour,
        customer=customer,
        status='approved',
        verified_booking=bool(verified_booking),
        booking=verified_booking
    )

    return Response({
        'message': 'Review submitted successfully!',
        'review': TourReviewSerializer(review, context={'request': request}).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def feature_sections(request):
    """List curated feature sections."""
    sections = FeatureSection.objects.filter(status='active').order_by('rank')
    serializer = FeatureSectionSerializer(sections, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def feature_section_detail(request, feature_id):
    """Get single feature section with tours."""
    section = get_object_or_404(FeatureSection, pk=feature_id, status='active')
    serializer = FeatureSectionSerializer(section, context={'request': request})
    return Response(serializer.data)


# ==============================================================================
# 4. DESTINATIONS & TAXONOMIES
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.filter(status='active').annotate(
        tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('display_order', 'name')
    return Response(CategorySerializer(categories, many=True, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def country_list(request):
    countries = Country.objects.filter(is_active=True).annotate(
        tour_count=Count('cities__tours', filter=Q(cities__tours__status='active'))
    ).order_by('name')
    return Response(CountrySerializer(countries, many=True, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def city_list(request):
    cities = City.objects.filter(is_active=True).annotate(
        tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('name')
    return Response(CitySerializer(cities, many=True, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def region_list(request):
    regions = DestinationRegion.objects.filter(is_active=True).annotate(
        tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('name')
    return Response(DestinationRegionSerializer(regions, many=True, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def supplier_list(request):
    suppliers = TourSupplier.objects.filter(status='active').annotate(
        tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('-rating', 'company_name')
    return Response(TourSupplierSerializer(suppliers, many=True, context={'request': request}).data)


# ==============================================================================
# 5. COUPONS & TOUR BOOKINGS
# ==============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_coupon(request):
    """Validate coupon code and return discount calculation."""
    code = request.data.get('code') or request.GET.get('code', '').strip()
    subtotal = request.data.get('subtotal', 0)
    try:
        subtotal = Decimal(str(subtotal))
    except Exception:
        subtotal = Decimal('0.00')

    if not code:
        return Response({'valid': False, 'message': 'Coupon code is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        coupon = Coupon.objects.get(
            code__iexact=code,
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_until__gte=timezone.now()
        )

        if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
            return Response({'valid': False, 'message': 'This coupon has reached its usage limit.'}, status=status.HTTP_200_OK)

        discount_amount = Decimal('0.00')
        if subtotal > Decimal('0.00'):
            if coupon.discount_type == 'percentage':
                discount_amount = subtotal * (coupon.discount_value / Decimal('100.0'))
                if coupon.max_discount_amount and discount_amount > coupon.max_discount_amount:
                    discount_amount = coupon.max_discount_amount
            else:
                discount_amount = min(coupon.discount_value, subtotal)

        return Response({
            'valid': True,
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': float(coupon.discount_value),
            'max_discount': float(coupon.max_discount_amount) if coupon.max_discount_amount else None,
            'calculated_discount': float(discount_amount)
        })

    except Coupon.DoesNotExist:
        return Response({'valid': False, 'message': 'Invalid or expired coupon code.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    """
    Create a tour booking.
    Accepts guest details or authenticates with request.user.
    Calculates participant prices, coupon discount, creates booking,
    and returns Flatpay/Frisbii payment checkout url or confirmation.
    """
    serializer = BookingCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    tour = get_object_or_404(Tour, pk=data['tour_id'], status='active')

    # Resolve user & customer
    user = request.user if request.user.is_authenticated else None
    contact_email = data['contact_email'].lower().strip()
    contact_name = data['contact_name'].strip()
    contact_phone = data.get('contact_phone', '').strip()

    if not user:
        user = User.objects.filter(email__iexact=contact_email).first()
        if not user:
            # Create user for guest
            random_pw = get_random_string(length=12)
            user = User.objects.create_user(
                username=contact_email,
                email=contact_email,
                password=random_pw,
                first_name=contact_name.split()[0] if contact_name else 'Guest',
                last_name=' '.join(contact_name.split()[1:]) if len(contact_name.split()) > 1 else ''
            )

    customer, _ = Customer.objects.get_or_create(
        user=user,
        defaults={'phone': contact_phone}
    )
    if contact_phone and not customer.phone:
        customer.phone = contact_phone
        customer.save()

    # Calculate participants & pricing
    participants_input = data['participants']
    subtotal = Decimal('0.00')
    participant_details = []
    created_participants_data = []

    for p in participants_input:
        p_type = p.get('participant_type') or p.get('type') or 'adult'
        age = p.get('age')

        pricing = None
        if age is not None:
            pricing = tour.pricing_options.filter(
                is_active=True,
                min_age__lte=age,
                max_age__gte=age
            ).first()

        if not pricing:
            pricing = tour.pricing_options.filter(participant_type=p_type, is_active=True).first()

        price = pricing.price if pricing else tour.base_price
        subtotal += price

        p_info = {
            'participant_type': p_type,
            'first_name': p.get('first_name', ''),
            'last_name': p.get('last_name', ''),
            'age': age,
            'email': p.get('email', ''),
            'phone': p.get('phone', ''),
            'special_requirements': p.get('special_requirements', ''),
            'price': str(price)
        }
        participant_details.append(p_info)
        created_participants_data.append((p_info, price))

    # Apply Coupon
    discount_amount = Decimal('0.00')
    applied_coupon = None
    coupon_code = data.get('coupon_code', '').strip()
    if coupon_code:
        try:
            applied_coupon = Coupon.objects.get(
                code__iexact=coupon_code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_until__gte=timezone.now()
            )
            if not applied_coupon.usage_limit or applied_coupon.used_count < applied_coupon.usage_limit:
                if applied_coupon.discount_type == 'percentage':
                    discount_amount = subtotal * (applied_coupon.discount_value / Decimal('100.0'))
                    if applied_coupon.max_discount_amount and discount_amount > applied_coupon.max_discount_amount:
                        discount_amount = applied_coupon.max_discount_amount
                else:
                    discount_amount = min(applied_coupon.discount_value, subtotal)
        except Coupon.DoesNotExist:
            pass

    tax_rate = Decimal('0.00')
    tax_amount = (subtotal - discount_amount) * tax_rate
    total_amount = max(Decimal('0.00'), subtotal - discount_amount + tax_amount)

    # Generate unique booking number
    while True:
        booking_number = 'BK' + ''.join(random.choices(string.digits, k=8))
        if not Booking.objects.filter(booking_number=booking_number).exists():
            break

    # Resolve time and time slot
    tour_time_val = data.get('tour_time') or None
    tour_time_slot_val = data.get('tour_time_slot')
    time_slot_obj = None
    if tour_time_slot_val:
        if isinstance(tour_time_slot_val, int) or (isinstance(tour_time_slot_val, str) and tour_time_slot_val.isdigit()):
            time_slot_obj = TourTimeSlot.objects.filter(pk=int(tour_time_slot_val)).first()
        elif isinstance(tour_time_slot_val, str):
            time_slot_obj = TourTimeSlot.objects.filter(tour=tour, time_slot__name__iexact=tour_time_slot_val).first()

    booking = Booking.objects.create(
        booking_number=booking_number,
        customer=customer,
        tour=tour,
        schedule_id=data.get('schedule_id'),
        tour_date=data['tour_date'],
        tour_time=tour_time_val,
        tour_time_slot=time_slot_obj,
        total_participants=len(participant_details),
        participant_details=participant_details,
        subtotal=subtotal,
        discount_amount=discount_amount,
        coupon=applied_coupon,
        tax_amount=tax_amount,
        total_amount=total_amount,
        currency=tour.currency,
        contact_name=contact_name,
        contact_email=contact_email,
        contact_phone=contact_phone,
        special_requirements=data.get('special_requirements', ''),
        pickup_location=data.get('pickup_location', ''),
        customer_notes=data.get('customer_notes', ''),
        country=data.get('country', ''),
        status='pending',
        payment_status='pending',
    )

    if applied_coupon:
        CouponUsage.objects.create(
            coupon=applied_coupon,
            customer=customer,
            booking=booking,
            discount_amount=discount_amount
        )
        applied_coupon.used_count += 1
        applied_coupon.save()

    for p_info, p_price in created_participants_data:
        BookingParticipant.objects.create(
            booking=booking,
            participant_type=p_info['participant_type'],
            first_name=p_info['first_name'],
            last_name=p_info['last_name'],
            age=p_info['age'],
            email=p_info['email'],
            phone=p_info['phone'],
            special_requirements=p_info['special_requirements'],
            price=p_price
        )

    # Handle Payment Gateway
    payment_url = None
    if getattr(settings, 'USE_PAYMENT_GATEWAY', False):
        api_key = getattr(settings, 'FLATPAY_KEY', '')
        url = 'https://checkout-api.frisbii.com/v1/session/charge'
        amount = int(float(total_amount) * 100)
        
        # Next.js frontend or backend webhook URLs
        accept_url = request.build_absolute_uri(f"/api/bookings/{booking_number}/payment/accept/")
        cancel_url = request.build_absolute_uri(f"/api/bookings/{booking_number}/payment/cancel/")
        
        charge_data = {
            'order': {
                'handle': booking_number,
                'amount': amount,
                'currency': 'USD',
                'customer': {
                    'email': contact_email,
                    'first_name': contact_name.split()[0] if contact_name else 'Guest',
                    'last_name': ' '.join(contact_name.split()[1:]) if len(contact_name.split()) > 1 else 'Guest',
                }
            },
            'accept_url': accept_url,
            'cancel_url': cancel_url
        }
        try:
            res = requests.post(url, auth=(api_key, ''), json=charge_data)
            res_json = res.json()
            payment_url = res_json.get('url')
        except Exception as e:
            logger.exception(f"Payment gateway error: {e}")

    return Response({
        'message': 'Booking created successfully.',
        'booking_number': booking.booking_number,
        'booking': BookingSerializer(booking, context={'request': request}).data,
        'payment_url': payment_url,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def booking_detail(request, booking_number):
    """Get booking confirmation and details by booking number."""
    booking = get_object_or_404(
        Booking.objects.select_related('tour', 'customer__user').prefetch_related('participants'),
        booking_number=booking_number
    )
    return Response(BookingSerializer(booking, context={'request': request}).data)


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def booking_payment_accept(request, booking_number):
    """Handles payment approval for booking."""
    booking = get_object_or_404(Booking, booking_number=booking_number)
    if booking.payment_status != 'paid':
        booking.payment_status = 'paid'
        booking.status = 'confirmed'
        booking.save()
        
    return Response({
        'status': 'success',
        'message': 'Payment confirmed.',
        'booking_number': booking_number,
        'payment_status': booking.payment_status,
        'booking_status': booking.status
    })


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def booking_payment_cancel(request, booking_number):
    """Handles payment cancellation for booking."""
    booking = get_object_or_404(Booking, booking_number=booking_number)
    if booking.payment_status != 'paid':
        booking.payment_status = 'failed'
        booking.status = 'cancelled'
        booking.save()

    return Response({
        'status': 'cancelled',
        'message': 'Payment cancelled.',
        'booking_number': booking_number,
        'payment_status': booking.payment_status,
        'booking_status': booking.status
    })


# ==============================================================================
# 6. BIKE RENTAL API
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def bike_list(request):
    """List all bikes available for rent with addons and pricing."""
    bikes = Bike.objects.prefetch_related('bike_addons__addon').all().order_by('rank')
    return Response(BikeSerializer(bikes, many=True, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def bike_detail(request, bike_id):
    """Get single bike detail by ID or slug."""
    bike = None
    target_id = parse_id_from_param(bike_id)
    if target_id:
        bike = Bike.objects.filter(pk=target_id).first()
    if not bike:
        bike = Bike.objects.filter(slug=bike_id).first()
    if not bike:
        return Response({'detail': 'Bike not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(BikeSerializer(bike, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_bike_booking(request):
    """Create bike rental booking."""
    serializer = BikeBookingCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    bike = get_object_or_404(Bike, pk=data['bike_id'])

    user = request.user if request.user.is_authenticated else None
    email = data['email'].lower().strip()
    name = data['name'].strip()
    phone = data['phone'].strip()
    address = data.get('address', '').strip()

    if not user:
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            pw = get_random_string(length=10)
            user = User.objects.create_user(
                username=email, email=email, password=pw,
                first_name=name.split()[0] if name else 'Guest'
            )

    customer, _ = Customer.objects.get_or_create(user=user, defaults={'phone': phone, 'address': address})

    booking = BikeBooking(
        customer=customer,
        bike=bike,
        name=name,
        email=email,
        phone=phone,
        address=address,
        other_info=data.get('other_info', ''),
        bike_quantity=data.get('bike_quantity', 1),
        start_date=data['start_date'],
        end_date=data['end_date'],
        start_time=data.get('start_time', ''),
        end_time=data.get('end_time', ''),
    )
    booking.save()
    booking.refresh_from_db()

    # Addons
    addons_input = data.get('addons', [])
    for a in addons_input:
        addon_id = a.get('addon_id')
        qty = int(a.get('quantity', 0))
        if addon_id and qty > 0:
            price_record = BikeAddonPrice.objects.filter(bike=bike, addon_id=addon_id).first()
            if price_record:
                BikeBookingAddon.objects.create(
                    booking=booking,
                    addon=price_record.addon,
                    price=price_record.price,
                    quantity=qty
                )

    total_addons = sum(item.total_price_with_days for item in booking.booking_addons.all())
    booking.subtotal = booking.bike_total_price_with_days + total_addons
    booking.total = booking.subtotal
    booking.save()

    payment_url = None
    if getattr(settings, 'USE_PAYMENT_GATEWAY', False):
        api_key = getattr(settings, 'FLATPAY_KEY', '')
        url = 'https://checkout-api.frisbii.com/v1/session/charge'
        amount = int(float(booking.total) * 100)
        accept_url = request.build_absolute_uri(f"/api/bikes/booking/{booking.booking_number}/payment/accept/")
        cancel_url = request.build_absolute_uri(f"/api/bikes/booking/{booking.booking_number}/payment/cancel/")
        
        charge_data = {
            'order': {
                'handle': booking.booking_number,
                'amount': amount,
                'currency': 'USD',
                'customer': {
                    'email': email,
                    'first_name': name.split()[0] if name else 'Guest',
                    'last_name': ' '.join(name.split()[1:]) if len(name.split()) > 1 else 'Guest',
                }
            },
            'accept_url': accept_url,
            'cancel_url': cancel_url
        }
        try:
            res = requests.post(url, auth=(api_key, ''), json=charge_data)
            payment_url = res.json().get('url')
        except Exception as e:
            logger.exception(f"Payment error: {e}")

    return Response({
        'message': 'Bike booking created successfully.',
        'booking_number': booking.booking_number,
        'booking': BikeBookingSerializer(booking, context={'request': request}).data,
        'payment_url': payment_url,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def bike_booking_detail(request, booking_number):
    booking = get_object_or_404(BikeBooking, booking_number=booking_number)
    return Response(BikeBookingSerializer(booking, context={'request': request}).data)


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def bike_payment_accept(request, booking_number):
    booking = get_object_or_404(BikeBooking, booking_number=booking_number)
    booking.paid = True
    booking.status = 'confirmed'
    booking.save()
    return Response({'status': 'success', 'message': 'Bike booking payment accepted.'})


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def bike_payment_cancel(request, booking_number):
    booking = get_object_or_404(BikeBooking, booking_number=booking_number)
    booking.status = 'cancelled'
    booking.save()
    return Response({'status': 'cancelled', 'message': 'Bike booking payment cancelled.'})


# ==============================================================================
# 7. SOUVENIRS & CART API
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def souvenir_list(request):
    souvenirs = Souvenir.objects.filter(status='active').order_by('-created_at')
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(souvenirs, request)
    serializer = SouvenirSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def souvenir_detail(request, souvenir_id):
    target_id = parse_id_from_param(souvenir_id)
    souvenir = get_object_or_404(Souvenir, pk=target_id or souvenir_id, status='active')
    return Response(SouvenirSerializer(souvenir, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def souvenir_pickup_locations(request):
    locations = SouvenirPickuplocation.objects.filter(status='active')
    return Response(SouvenirPickuplocationSerializer(locations, many=True, context={'request': request}).data)


# Cart Management (Session & Next.js friendly)
@api_view(['GET'])
@permission_classes([AllowAny])
def cart_get(request):
    cart = request.session.get('cart', {})
    setting = SiteSetting.get_settings()
    shipping_charge = float(setting.shipping_charge) if setting and setting.shipping_charge else 0.0

    items = []
    subtotal = 0.0
    for s_id, item in cart.items():
        line_total = item['price'] * item['quantity']
        subtotal += line_total
        items.append({
            'souvenir_id': int(s_id),
            'title': item['title'],
            'price': item['price'],
            'image': item.get('image', ''),
            'quantity': item['quantity'],
            'total': line_total
        })

    return Response({
        'items': items,
        'item_count': sum(i['quantity'] for i in items),
        'subtotal': subtotal,
        'shipping_charge': shipping_charge,
        'total': subtotal + shipping_charge
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def cart_add(request):
    souvenir_id = request.data.get('souvenir_id')
    quantity = int(request.data.get('quantity', 1))
    souvenir = get_object_or_404(Souvenir, pk=souvenir_id, status='active')

    cart = request.session.get('cart', {})
    s_id = str(souvenir.id)

    if s_id in cart:
        cart[s_id]['quantity'] += quantity
    else:
        cart[s_id] = {
            'title': souvenir.title,
            'price': float(souvenir.price),
            'image': request.build_absolute_uri(souvenir.image.url) if souvenir.image else '',
            'quantity': quantity
        }

    request.session['cart'] = cart
    request.session.modified = True
    return Response({'message': 'Added to cart.', 'cart': cart})


@api_view(['POST'])
@permission_classes([AllowAny])
def cart_update(request):
    souvenir_id = str(request.data.get('souvenir_id'))
    quantity = int(request.data.get('quantity', 1))

    cart = request.session.get('cart', {})
    if souvenir_id in cart:
        if quantity <= 0:
            del cart[souvenir_id]
        else:
            cart[souvenir_id]['quantity'] = quantity
        request.session['cart'] = cart
        request.session.modified = True

    return Response({'message': 'Cart updated.', 'cart': cart})


@api_view(['POST'])
@permission_classes([AllowAny])
def cart_remove(request):
    souvenir_id = str(request.data.get('souvenir_id'))
    cart = request.session.get('cart', {})
    if souvenir_id in cart:
        del cart[souvenir_id]
        request.session['cart'] = cart
        request.session.modified = True

    return Response({'message': 'Item removed from cart.', 'cart': cart})


@api_view(['POST'])
@permission_classes([AllowAny])
def cart_clear(request):
    request.session['cart'] = {}
    request.session.modified = True
    return Response({'message': 'Cart cleared.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def cart_checkout(request):
    """
    Checkout souvenirs order.
    Supports either session cart or explicitly passed items payload:
    `[{'souvenir_id': 1, 'quantity': 2}]`
    """
    serializer = SouvenirOrderCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    items_input = data.get('items')
    cart = request.session.get('cart', {})

    # Build order items list
    order_items_to_create = []
    subtotal = Decimal('0.00')

    if items_input:
        for item in items_input:
            s = get_object_or_404(Souvenir, pk=item['souvenir_id'])
            qty = int(item['quantity'])
            subtotal += s.price * qty
            order_items_to_create.append((s, s.price, qty))
    elif cart:
        for s_id, item in cart.items():
            s = get_object_or_404(Souvenir, pk=int(s_id))
            qty = int(item['quantity'])
            subtotal += s.price * qty
            order_items_to_create.append((s, s.price, qty))
    else:
        return Response({'detail': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

    setting = SiteSetting.get_settings()
    shipping_charge = Decimal('0.00')
    if data['delivery_method'] != 'pickup':
        shipping_charge = Decimal(str(setting.shipping_charge or 0.0))

    total_amount = subtotal + shipping_charge
    order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    customer = None
    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        customer = request.user.customer_profile

    order = SouvenirOrder.objects.create(
        order_number=order_number,
        customer=customer,
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data['phone'],
        address=data.get('address', ''),
        city=data.get('city', ''),
        postal_code=data.get('postal_code', ''),
        delivery_method=data['delivery_method'],
        pickup_location_id=data.get('pickup_location_id'),
        pickup_date=data.get('pickup_date'),
        pickup_time=data.get('pickup_time'),
        shipping_charge=shipping_charge,
        total_amount=total_amount,
        status='pending'
    )

    for souvenir, price, qty in order_items_to_create:
        SouvenirOrderItem.objects.create(
            order=order,
            souvenir=souvenir,
            price=price,
            quantity=qty
        )

    # Clear session cart if used
    request.session['cart'] = {}
    request.session.modified = True

    return Response({
        'message': 'Order placed successfully.',
        'order_number': order.order_number,
        'order': SouvenirOrderSerializer(order, context={'request': request}).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def order_detail(request, order_number):
    order = get_object_or_404(SouvenirOrder.objects.prefetch_related('items__souvenir'), order_number=order_number)
    return Response(SouvenirOrderSerializer(order, context={'request': request}).data)


# ==============================================================================
# 8. BLOG API
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def blog_list(request):
    blogs = BlogPost.objects.filter(status='published').order_by('-created_at')
    
    category = request.GET.get('category')
    if category:
        cat_id = parse_id_from_param(category)
        if cat_id:
            blogs = blogs.filter(category_id=cat_id)
        else:
            blogs = blogs.filter(category__slug=category)

    search = request.GET.get('search') or request.GET.get('q')
    if search:
        blogs = blogs.filter(Q(title__icontains=search) | Q(content__icontains=search))

    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(blogs, request)
    serializer = BlogPostListSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def blog_detail(request, blog_id):
    blog = None
    target_id = parse_id_from_param(blog_id)
    if target_id:
        blog = BlogPost.objects.filter(pk=target_id, status='published').first()
    if not blog:
        blog = BlogPost.objects.filter(slug=blog_id, status='published').first()
    if not blog:
        return Response({'detail': 'Blog post not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Increment view count
    blog.view_count += 1
    blog.save(update_fields=['view_count'])

    return Response(BlogPostDetailSerializer(blog, context={'request': request}).data)


# ==============================================================================
# 9. CMS PAGES, FAQS, REVIEWS, TEAM
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def page_list(request):
    pages = Page.objects.filter(is_active=True).order_by('title')
    return Response(PageListSerializer(pages, many=True, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def page_detail(request, page_slug):
    page = None
    target_id = parse_id_from_param(page_slug)
    if target_id:
        page = Page.objects.filter(pk=target_id, is_active=True).first()
    if not page:
        page = Page.objects.filter(slug=page_slug, is_active=True).first()
    if not page:
        return Response({'detail': 'Page not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(PageDetailSerializer(page, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def testimonials(request):
    static_reviews = CustomerReviewStatic.objects.filter(is_active=True).order_by('display_order', '-created_at')
    tour_reviews = TourReview.objects.filter(status='approved').select_related('customer__user', 'tour').order_by('-created_at')[:20]

    return Response({
        'static_testimonials': CustomerReviewStaticSerializer(static_reviews, many=True, context={'request': request}).data,
        'tour_reviews': TourReviewSerializer(tour_reviews, many=True, context={'request': request}).data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def faq_list(request):
    faqs = FAQ.objects.filter(status='active').order_by('display_order')
    return Response(FAQSerializer(faqs, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def team_members(request):
    members = TeamMember.objects.all().order_by('-created_at')
    return Response(TeamMemberSerializer(members, many=True, context={'request': request}).data)


# ==============================================================================
# 10. CONTACT US & NEWSLETTER
# ==============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def contact_submit(request):
    serializer = ContactUsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Thank you! Your message has been received.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def newsletter_subscribe(request):
    email = request.data.get('email', '').strip().lower()
    name = request.data.get('name', '').strip()
    if not email:
        return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    subscriber, created = Newsletter.objects.get_or_create(
        email=email,
        defaults={'name': name, 'is_active': True}
    )
    if not created and not subscriber.is_active:
        subscriber.is_active = True
        subscriber.save()

    return Response({'message': 'Subscribed successfully to the newsletter.'}, status=status.HTTP_200_OK)


# ==============================================================================
# 11. AI CHATBOT PROXY
# ==============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def ai_chat(request):
    """
    AI Chat endpoint for Next.js.
    Accepts: { 'message': str, 'history': [{'sender': 'user'|'bot', 'text': str}] }
    Delegates to the local transformers pipeline or returns a fallback assistant reply.
    """
    user_message = request.data.get('message', '').strip()
    history = request.data.get('history', [])

    if not user_message:
        return Response({'detail': 'Message is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        from Yourtourguide.ai_views import get_chatbot_pipeline, normalize_question
        
        prompt_parts = []
        for msg in history:
            sender = "User" if msg.get("sender") == "user" else "CopenhagenMemories"
            text = normalize_question(msg.get("text", ""))
            prompt_parts.append(f"{sender}: {text}")

        normalized_message = normalize_question(user_message)
        prompt_parts.append(f"User: {normalized_message}")
        prompt_parts.append("CopenhagenMemories:")
        prompt = "\n".join(prompt_parts)

        chatbot = get_chatbot_pipeline()
        response = chatbot(
            prompt,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            pad_token_id=chatbot.tokenizer.eos_token_id
        )
        generated_text = response[0]['generated_text']
        if generated_text.startswith(prompt):
            reply = generated_text[len(prompt):].strip()
        else:
            reply = generated_text.strip()

        return Response({'reply': reply})
    except Exception as e:
        logger.warning(f"AI chat fallback: {e}")
        # Graceful fallback response so frontend works even without heavy torch models
        return Response({
            'reply': f"Welcome to Copenhagen Memories! How can I assist you with exploring Copenhagen or booking our guided tours?"
        })


# ==============================================================================
# 12. CUSTOMER AUTH & USER MANAGEMENT (FOR NEXT.JS)
# ==============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def customer_register(request):
    """Register customer account and return auth token."""
    serializer = CustomerRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user = User.objects.create_user(
        username=data['email'],
        email=data['email'],
        password=data['password'],
        first_name=data['first_name'],
        last_name=data.get('last_name', '')
    )

    customer, _ = Customer.objects.get_or_create(
        user=user,
        defaults={'phone': data.get('phone', '')}
    )

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'token': token.key,
        'user': CustomerUserSerializer(user, context={'request': request}).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def customer_login(request):
    """Authenticate customer and return auth token."""
    serializer = CustomerLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email'].lower()
    password = serializer.validated_data['password']

    user = authenticate(request, username=email, password=password)
    if not user:
        return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': CustomerUserSerializer(user, context={'request': request}).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customer_logout(request):
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'message': 'Logged out successfully.'})


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def customer_profile(request):
    """Get or update current customer profile."""
    customer, _ = Customer.objects.get_or_create(user=request.user)

    if request.method == 'PUT':
        serializer = CustomerProfileUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        if 'first_name' in d:
            request.user.first_name = d['first_name']
        if 'last_name' in d:
            request.user.last_name = d['last_name']
        request.user.save()

        if 'phone' in d:
            customer.phone = d['phone']
        if 'address' in d:
            customer.address = d['address']
        if 'preferred_language' in d:
            customer.preferred_language = d['preferred_language']
        customer.save()

    return Response(CustomerUserSerializer(request.user, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_bookings(request):
    """List bookings for the authenticated customer."""
    bookings = Booking.objects.filter(customer__user=request.user).order_by('-created_at')
    serializer = BookingSerializer(bookings, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_bike_bookings(request):
    """List bike bookings for the authenticated customer."""
    bookings = BikeBooking.objects.filter(customer__user=request.user).order_by('-created_at')
    serializer = BikeBookingSerializer(bookings, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_orders(request):
    """List souvenir orders for the authenticated customer."""
    orders = SouvenirOrder.objects.filter(customer__user=request.user).order_by('-created_at')
    serializer = SouvenirOrderSerializer(orders, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_wishlist(request):
    """List customer wishlisted tours."""
    customer, _ = Customer.objects.get_or_create(user=request.user)
    wishlist = Wishlist.objects.filter(customer=customer).select_related('tour__supplier', 'tour__city', 'tour__category')
    return Response(WishlistSerializer(wishlist, many=True, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_wishlist(request):
    """Toggle tour in customer wishlist."""
    tour_id = request.data.get('tour_id')
    tour = get_object_or_404(Tour, pk=tour_id)
    customer, _ = Customer.objects.get_or_create(user=request.user)

    item = Wishlist.objects.filter(customer=customer, tour=tour).first()
    if item:
        item.delete()
        return Response({'in_wishlist': False, 'message': 'Tour removed from wishlist.'})
    else:
        Wishlist.objects.create(customer=customer, tour=tour)
        return Response({'in_wishlist': True, 'message': 'Tour added to wishlist.'})
