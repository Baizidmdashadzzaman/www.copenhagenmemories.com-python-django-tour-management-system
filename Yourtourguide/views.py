from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Value
from django.db.models.functions import Coalesce
from accounts.models import Tour, Category, DestinationRegion, City, TourReview

from accounts.models import BlogPost, ContactUs, SiteSetting, CustomerReviewStatic, FAQ, TourSupplier, Country, FeatureSection, Slider,Page, Tour, TeamMember, Souvenir, Bike
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import translation, timezone
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.crypto import get_random_string

import logging
logger = logging.getLogger(__name__)

def rent_bike(request):
    from django.contrib import messages
    from accounts.models import Customer, BikeBooking, BikeBookingAddon, Bike
    from django.contrib.auth.models import User
    from django.utils.crypto import get_random_string

    if request.method == 'POST':
        bike_id = request.POST.get('bike_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        bike_quantity = request.POST.get('bike_quantity', 1)
        other_info = request.POST.get('other_info', '')

        bike = get_object_or_404(Bike, id=bike_id)
        
        customer = None
        user = request.user
        
        if not user.is_authenticated:
            if email:
                user_exists = User.objects.filter(email=email).exists()
                if user_exists:
                    user = User.objects.get(email=email)
                else:
                    password = get_random_string(length=10)
                    username = email
                    try:
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            first_name=name or 'Guest'
                        )
                        # Optional: send email here
                    except Exception as e:
                        messages.error(request, f"Error creating account: {str(e)}")
                        user = None
        
        if user:
            try:
                customer, created = Customer.objects.get_or_create(
                    user=user,
                    defaults={
                        'phone': phone,
                    }
                )
                if not created and not customer.phone and phone:
                    customer.phone = phone
                if not customer.address and address:
                    customer.address = address
                customer.save()
            except Exception as e:
                messages.error(request, f"Error with customer profile: {str(e)}")

        try:
            booking = BikeBooking(
                customer=customer,  # can be none if user creation failed, though model allows null
                name=name,
                email=email,
                phone=phone,
                address=address,
                other_info=other_info,
                bike=bike,
                bike_quantity=int(bike_quantity) if bike_quantity else 1,
            )
            if start_date:
                booking.start_date = start_date
            if end_date:
                booking.end_date = end_date
            if start_time:
                booking.start_time = start_time
            if end_time:
                booking.end_time = end_time
                
            booking.save()
            booking.refresh_from_db()
            
            # Process Addons
            for ba in bike.bike_addons.all():
                quantity_str = request.POST.get(f'addon_quantity_{ba.id}', '0')
                try:
                    qty = int(quantity_str)
                    if qty > 0:
                        BikeBookingAddon.objects.create(
                            booking=booking,
                            addon=ba.addon,
                            price=ba.price,
                            quantity=qty
                        )
                except ValueError:
                    pass
            
            # Update the totals
            total_addons = sum(addon.total_price_with_days for addon in booking.booking_addons.all())
            booking.subtotal = booking.bike_total_price_with_days + total_addons
            booking.total = booking.subtotal
            booking.save()
            
            if getattr(settings, 'USE_PAYMENT_GATEWAY', False):
                import requests
                from django.urls import reverse
                
                api_key = getattr(settings, 'FLATPAY_KEY', '')
                url = 'https://checkout-api.frisbii.com/v1/session/charge'
                
                amount = int(float(booking.total) * 100)
                accept_url = request.build_absolute_uri(reverse('rent_bike_payment_accept', args=[booking.booking_number]))
                cancel_url = request.build_absolute_uri(reverse('rent_bike_payment_cancel', args=[booking.booking_number]))
                
                data = {
                    'order': {
                        'handle': booking.booking_number,
                        'amount': amount,
                        'currency': 'USD',
                        'customer': {
                            'email': booking.email,
                            'first_name': booking.name.split()[0] if booking.name else 'Guest',
                            'last_name': ' '.join(booking.name.split()[1:]) if booking.name and len(booking.name.split()) > 1 else 'Guest',
                        }
                    },
                    'accept_url': accept_url,
                    'cancel_url': cancel_url
                }
                
                try:
                    response = requests.post(url, auth=(api_key, ''), json=data)
                    response_data = response.json()
                    if 'url' in response_data:
                        return redirect(response_data['url'])
                    else:
                        messages.error(request, f"Payment gateway error: {response_data.get('error', 'Unknown error')}")
                        return redirect('rent_bike_confirmation', booking_number=booking.booking_number)
                except Exception as e:
                    messages.error(request, f"Payment gateway error: {str(e)}")
                    return redirect('rent_bike_confirmation', booking_number=booking.booking_number)
            else:
                messages.success(request, f'Your bike booking has been submitted successfully! Booking Number: {booking.booking_number}')
                return redirect('rent_bike_confirmation', booking_number=booking.booking_number)
        except Exception as e:
            messages.error(request, f'An error occurred while booking: {str(e)}')

    bikes = Bike.objects.prefetch_related('bike_addons__addon').all().order_by('rank')
    context = {
        'bikes': bikes,
    }
    return render(request, 'frontend/pages/rent-bike/rent_bike_list.html', context)

def rent_bike_confirmation(request, booking_number):
    from accounts.models import BikeBooking
    booking = get_object_or_404(BikeBooking.objects.prefetch_related('booking_addons__addon'), booking_number=booking_number)
    context = {
        'booking': booking,
    }
    return render(request, 'frontend/pages/rent-bike/confirmation.html', context)

def rent_bike_payment_accept(request, booking_number):
    from accounts.models import BikeBooking
    from django.contrib import messages
    import requests
    
    booking = get_object_or_404(BikeBooking, booking_number=booking_number)
    
    if getattr(settings, 'USE_PAYMENT_GATEWAY', False):
        api_key = getattr(settings, 'FLATPAY_KEY', '')
        url = f"https://api.frisbii.com/v1/charge/{booking_number}"
        try:
            response = requests.get(url, auth=(api_key, ''), headers={'Accept': 'application/json'})
            data = response.json()
            if response.status_code == 200 and data.get('state') not in ['authorized', 'settled']:
                messages.error(request, "Payment was not authorized.")
                return redirect('rent_bike')
        except Exception as e:
            pass
            
    if booking.status != 'confirmed':
        booking.status = 'confirmed'
        booking.save()

    try:
        send_mail(
            'New Bike Rent Booking',
            f'Booking Number: {booking.booking_number}',
            settings.DEFAULT_FROM_EMAIL,
            ['contact@copenhagenmemories.com'],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Admin email failed: {str(e)}")
        
    messages.success(request, f'Payment successful! Your bike booking confirmed. Booking Number: {booking.booking_number}')
    return redirect('rent_bike_confirmation', booking_number=booking.booking_number)

def rent_bike_payment_cancel(request, booking_number):
    from accounts.models import BikeBooking
    from django.contrib import messages
    
    booking = get_object_or_404(BikeBooking, booking_number=booking_number)
    if booking.status != 'confirmed':
        booking.status = 'cancelled'
        booking.save()
        
    messages.warning(request, "Payment was cancelled.")
    return redirect('rent_bike')

def send_test_email(request):
    try:
        send_mail(
            subject='Test Email from Django',
            message='This is a test email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['ashad0167@gmail.com'],
        fail_silently=False,
    )
    except Exception as e:
        return HttpResponse(f"Email sent {e}")

    return HttpResponse("Email sent")


def page_view(request, page_id, page_slug):
    page = get_object_or_404(Page, pk=page_id, slug=page_slug, is_active=True)
    context = {
        'page': page,
    }
    return render(request, 'frontend/pages/page/page_view.html', context)

def tour_countries(request):
    countries_list = Country.objects.filter(is_active=True).annotate(
        tour_count=Count('cities__tours', filter=Q(cities__tours__status='active'))
    ).order_by('name')
    paginator = Paginator(countries_list, 12)  
    page_number = request.GET.get('page')
    countries = paginator.get_page(page_number)
    context = {
        'countries': countries,
    }
    return render(request, 'frontend/pages/tour/tour_countries.html', context)


def tour_cities(request):
    cities_list = City.objects.filter(is_active=True).annotate(
        tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('name')
    paginator = Paginator(cities_list, 12)  
    page_number = request.GET.get('page')
    cities = paginator.get_page(page_number)
    context = {
        'cities': cities,
    }
    return render(request, 'frontend/pages/tour/tour_cities.html', context)


def tour_providers(request):
    suppliers_qs = TourSupplier.objects.filter(status='active').annotate(
        tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('-tour_count', 'company_name')

    paginator = Paginator(suppliers_qs, 12)
    page_number = request.GET.get('page')
    suppliers = paginator.get_page(page_number)

    context = {
        'suppliers': suppliers,
    }
    return render(request, 'frontend/pages/tour/tour_tourproviders.html', context)

def tour_destination_regions(request):
    destination_regions_list = DestinationRegion.objects.filter(is_active=True).annotate(
        tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('name')
    paginator = Paginator(destination_regions_list, 12)  
    page_number = request.GET.get('page')
    destination_regions = paginator.get_page(page_number)
    context = {
        'destination_regions': destination_regions,
    }
    return render(request, 'frontend/pages/tour/tour_destination_regions.html', context)



def set_language(request, lang_code):
    if lang_code in ['en', 'dk']:
        request.session['lang'] = lang_code
        translation.activate(lang_code)
        request.session['_language'] = lang_code  
    return redirect(request.META.get('HTTP_REFERER', '/'))


def blog_list(request):
    blogs = BlogPost.objects.filter(status='published').order_by('-created_at')
    paginator = Paginator(blogs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'frontend/pages/blog/blog_list.html', context)

def blog_detail(request, blog_id):
    if isinstance(blog_id, str):
        blog_id = int(blog_id.split('-')[-1])
    else:
        blog_id = int(blog_id)

    blog = get_object_or_404(BlogPost, pk=blog_id)
    context = {
        'blog': blog,
    }
    return render(request, 'frontend/pages/blog/blog_detail.html', context)

def home(request):
    
    # logger.exception(f"Home log check")

    reviews = CustomerReviewStatic.objects.filter(is_active=True).order_by('display_order', '-created_at')
    featured_blogs = BlogPost.objects.filter(status='published', is_featured=True).order_by('-created_at')
    faqs = FAQ.objects.filter(status='active', is_featured=True).order_by('display_order', '-created_at')
    
    cities = City.objects.filter(is_active=True).annotate(tour_count=Count('tours', filter=Q(tours__status='active'))).order_by('name')
    categories = Category.objects.filter(status='active').annotate(tour_count=Count('tours', filter=Q(tours__status='active'))).order_by('display_order', 'name')
    tour_suppliers = TourSupplier.objects.filter(status='active').annotate(tour_count=Count('tours', filter=Q(tours__status='active'))).order_by('-rating', 'company_name')
    destination_regions = DestinationRegion.objects.filter(is_active=True).annotate(tour_count=Count('tours', filter=Q(tours__status='active'))).order_by('name')
    countries = Country.objects.filter(is_active=True).annotate(tour_count=Count('cities__tours', filter=Q(cities__tours__status='active'))).order_by('name')
    feature_sections = FeatureSection.objects.filter(status='active').prefetch_related(
        Prefetch('section_tours__tour', queryset=Tour.objects.filter(status='active').annotate(
            calculated_average_rating=Coalesce(Avg('reviews__overall_rating'), Value(0.0)),
            calculated_total_reviews=Count('reviews')
        ).select_related(
            'supplier',
            'city__country',
            'destination_region'
        ).prefetch_related('images')),
    ).order_by('rank', '-created_at')
    sliders = Slider.objects.filter(status='active').order_by('-created_at')
    team_members = TeamMember.objects.all().order_by('-created_at')
    
    all_tours = Tour.objects.filter(status='active').annotate(
        calculated_average_rating=Coalesce(Avg('reviews__overall_rating'), Value(0.0)),
        calculated_total_reviews=Count('reviews')
    ).select_related(
        'supplier', 'category', 'destination_region', 'city', 'city__country'
    ).prefetch_related('images').order_by('rank')[:12]
    
    souvenirs = Souvenir.objects.filter(status='active').order_by('-created_at')[:8]
    
    context = {
        'reviews': reviews,
        'featured_blogs': featured_blogs,
        'faqs': faqs,
        'cities': cities,
        'categories': categories,
        'tour_suppliers': tour_suppliers,
        'destination_regions': destination_regions,
        'countries': countries,
        'feature_sections': feature_sections,
        'sliders': sliders,
        'all_tours': all_tours,
        'team_members': team_members,
        'souvenirs': souvenirs,
    }

    return render(request, 'frontend/pages/home.html', context)

def sitemap(request):
    # Static Pages
    static_pages = [
        {'name': 'Home', 'url_name': 'home'},
        {'name': 'All Tours', 'url_name': 'tour_list_fronted'},
        {'name': 'Find Tour', 'url_name': 'find_tour'},
        {'name': 'Tour Providers', 'url_name': 'tour_providers_fronted'},
        {'name': 'Destinations (Countries)', 'url_name': 'tour_countries_fronted'},
        {'name': 'Destinations (Cities)', 'url_name': 'tour_cities_fronted'},
        {'name': 'Destinations (Regions)', 'url_name': 'tour_destination_regions_fronted'},
        {'name': 'Blog', 'url_name': 'blog_list_fronted'},
        {'name': 'Contact Us', 'url_name': 'contactus'},
        {'name': 'Customer Login', 'url_name': 'customer_login'},
        {'name': 'Customer Register', 'url_name': 'register_customer'},
        {'name': 'Testimonial', 'url_name': 'testimonial'},
    ]

    # Dynamic Pages
    tours = Tour.objects.filter(status='active').select_related('city', 'destination_region').only('id', 'title', 'slug', 'city', 'destination_region')
    blogs = BlogPost.objects.filter(status='published').only('id', 'title', 'slug')
    pages = Page.objects.filter(is_active=True).only('id', 'title', 'slug')
    
    # Destinations
    countries = Country.objects.filter(is_active=True).order_by('name')
    destination_regions = DestinationRegion.objects.filter(is_active=True).order_by('name')
    cities = City.objects.filter(is_active=True).order_by('name')
    
    # Categories
    categories = Category.objects.filter(status='active').order_by('name')

    context = {
        'static_pages': static_pages,
        'tours': tours,
        'blogs': blogs,
        'pages': pages,
        'countries': countries,
        'destination_regions': destination_regions,
        'cities': cities,
        'categories': categories,
    }
    return render(request, 'frontend/pages/sitemap.html', context)

def contactus(request):
    from django.contrib import messages
    
    # Get site settings for contact information
    site_settings = SiteSetting.get_settings()
    
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validate required fields
        if name and email and message:
            try:
                # Save to database
                ContactUs.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    subject=subject,
                    message=message
                )

                # Send email notification
                email_subject = f"New Contact Us Submission: {subject or 'No Subject'}"
                email_body = f"""
                You have a new contact form submission:

                Name: {name}
                Email: {email}
                Phone: {phone}
                Subject: {subject}

                Message:
                {message}
                """
                
                try:
                    send_mail(
                        email_subject,
                        email_body,
                        settings.DEFAULT_FROM_EMAIL,
                        ['copenhagenmemories@gmail.com'],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(e)

                messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'site_settings': site_settings,
    }
    return render(request, 'frontend/pages/contactus.html', context)

def _build_tour_list_context(request):
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    supplier_id = request.GET.get('supplier', '')
    country_id = request.GET.get('country', '')
    region_id = request.GET.get('region', '')
    city_id = request.GET.get('city', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort', 'recommended')
    
    # New filters
    rating = request.GET.get('rating', '')
    difficulty = request.GET.get('difficulty', '')
    guests = request.GET.get('guests', '')
    start_date = request.GET.get('start_date', '')
    
    # Feature filters (checkboxes)
    features = {
        'live_guide': request.GET.get('live_guide'),
        'skip_the_line': request.GET.get('skip_the_line'),
        'instant_confirmation': request.GET.get('instant_confirmation'),
        'wheelchair_accessible': request.GET.get('wheelchair_accessible'),
        'mobile_ticket': request.GET.get('mobile_ticket'),
        'free_cancellation': request.GET.get('free_cancellation'),
    }

    # Base queryset with related data
    tours = Tour.objects.annotate(
        calculated_average_rating=Coalesce(Avg('reviews__overall_rating'), Value(0.0)),
        calculated_total_reviews=Count('reviews')
    ).select_related(
        'supplier', 'category', 'destination_region', 'city'
    ).prefetch_related(
        'images', 'reviews'
    ).filter(status='active')

    # Apply search filter
    if search_query:
        tours = tours.filter(
            Q(title__icontains=search_query) |
            Q(title_dk__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(city__name__icontains=search_query) |
            Q(destination_region__name__icontains=search_query)
        )

    # Apply category filter
    if category_id:
        tours = tours.filter(category_id=category_id)

    # Apply country filter (via city relation)
    if country_id:
        tours = tours.filter(city__country_id=country_id)

    # Apply region filter
    if region_id:
        tours = tours.filter(destination_region_id=region_id)

    # Apply city filter
    if city_id:
        tours = tours.filter(city_id=city_id)

    # Apply supplier filter
    if supplier_id:
        tours = tours.filter(supplier_id=supplier_id)

    # Apply price filter
    if min_price:
        tours = tours.filter(base_price__gte=min_price)
    if max_price:
        tours = tours.filter(base_price__lte=max_price)
        
    # Apply rating filter
    if rating:
        tours = tours.filter(calculated_average_rating__gte=rating)

    # Apply difficulty filter
    if difficulty:
        tours = tours.filter(difficulty_level=difficulty)

    # Apply guests filter
    if guests:
        try:
            guest_count = int(guests)
            tours = tours.filter(max_participants__gte=guest_count)
        except ValueError:
            pass

    # Apply date filter (basic implementation - checking if tour has schedules in range or is generally available)
    if start_date:
        # This is a simplified check. A more robust one would check TourSchedule availability.
        # For now, we assume if a start date is provided, we might filter by available_days or specific schedule existence
        pass 

    # Apply feature filters
    for feature, value in features.items():
        if value:
            filter_kwargs = {feature: True}
            tours = tours.filter(**filter_kwargs)

    # Apply sorting
    if sort_by == 'price_low':
        tours = tours.order_by('base_price')
    elif sort_by == 'price_high':
        tours = tours.order_by('-base_price')
    elif sort_by == 'rating':
        tours = tours.order_by('-calculated_average_rating')
    elif sort_by == 'newest':
        tours = tours.order_by('-created_at')
    else:  # recommended - featured tours first, then by rating
        tours = tours.order_by('rank', '-is_featured', '-calculated_average_rating', '-created_at')

    # Capture total before pagination
    total_tours = tours.count()

    # Pagination
    paginator = Paginator(tours, 12)  # 12 tours per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options
    categories = Category.objects.filter(status='active').annotate(
        active_tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('name')
    regions = DestinationRegion.objects.filter(is_active=True).annotate(
        active_tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('name')
    cities = City.objects.filter(is_active=True).annotate(
        active_tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('name')
    countries = Country.objects.filter(is_active=True).annotate(
        active_tour_count=Count('cities__tours', filter=Q(cities__tours__status='active'))
    ).order_by('name')
    suppliers = TourSupplier.objects.filter(status='active').annotate(
        active_tour_count=Count('tours', filter=Q(tours__status='active'))
    ).order_by('company_name')
    
    # Difficulty choices for filter
    difficulty_choices = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
        ('extreme', 'Extreme')
    ]

    selected_country = Country.objects.filter(pk=country_id).first() if country_id else None
    selected_region = DestinationRegion.objects.filter(pk=region_id).first() if region_id else None
    selected_city = City.objects.filter(pk=city_id).first() if city_id else None

    location_label = None
    if selected_city:
        location_label = selected_city.name
    elif selected_region:
        location_label = selected_region.name
    elif selected_country:
        location_label = selected_country.name

    wishlisted_tours = []
    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        from accounts.models import Wishlist
        wishlisted_tours = list(Wishlist.objects.filter(customer=request.user.customer_profile).values_list('tour_id', flat=True))

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_id': category_id,
        'supplier_id': supplier_id,
        'country_id': country_id,
        'region_id': region_id,
        'city_id': city_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'rating': rating,
        'difficulty': difficulty,
        'guests': guests,
        'start_date': start_date,
        'features': features,
        'categories': categories,
        'regions': regions,
        'cities': cities,
        'countries': countries,
        'suppliers': suppliers,
        'difficulty_choices': difficulty_choices,
        'total_tours': total_tours,
        'selected_country': selected_country,
        'selected_region': selected_region,
        'selected_city': selected_city,
        'location_label': location_label,
        'wishlisted_tours': wishlisted_tours,
    }

    return context


def tour_list(request, template_name='frontend/pages/tour/tour_list.html'):
    context = _build_tour_list_context(request)
    return render(request, template_name, context)


def tour_list_type_filtered(request):
    context = _build_tour_list_context(request)
    return render(request, 'frontend/pages/tour/tour_list_type_filltered.html', context)


def find_tour_page(request):
    context = _build_tour_list_context(request)
    return render(request, 'frontend/pages/tour/find_tour_page.html', context)


def validate_coupon(request):
    from django.http import JsonResponse
    from django.utils import timezone
    from accounts.models import Coupon
    
    code = request.GET.get('code', '').strip()
    
    if not code:
        return JsonResponse({'valid': False, 'message': 'Coupon code is required.'})
        
    try:
        coupon = Coupon.objects.get(
            code=code,
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_until__gte=timezone.now()
        )
        
        if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
            return JsonResponse({'valid': False, 'message': 'This coupon has reached its usage limit.'})
            
        return JsonResponse({
            'valid': True,
            'discount_type': coupon.discount_type,
            'discount_value': float(coupon.discount_value),
            'max_discount': float(coupon.max_discount_amount) if coupon.max_discount_amount else None
        })
        
    except Coupon.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Invalid or expired coupon code.'})

def tour_detail(request, tour_id):
    from .forms import FrontendBookingForm
    from accounts.models import Customer, Coupon, Booking, BookingParticipant
    from django.contrib import messages
    from django.contrib.auth.models import User
    import json
    from decimal import Decimal
    import random
    import string
    from django.db.models import Avg, Count, Value
    from django.db.models.functions import Coalesce
    from django.utils import timezone


    if isinstance(tour_id, str):
        tour_id = int(tour_id.split('-')[-1])
    else:
        tour_id = int(tour_id)

    # Get tour with all related data
    tour = get_object_or_404(
        Tour.objects.select_related(
            'supplier', 'category', 'destination_region', 'city'
        ).annotate(
            calculated_average_rating=Coalesce(Avg('reviews__overall_rating'), Value(0.0)),
            calculated_total_reviews=Count('reviews')
        ).prefetch_related(
            'images', 'highlights', 'included_items', 'excluded_items',
            'itinerary_steps', 'requirements', 'faqs', 'pricing_options',
            'schedules'
        ),
        pk=tour_id,
        status='active'
    )

    # Get related tours (same category or region)
    related_tours = Tour.objects.select_related(
        'supplier', 'category', 'destination_region', 'city'
    ).prefetch_related('images').filter(
        status='active'
    ).exclude(pk=tour_id)

    # Filter by category first, then by region if no category matches
    if tour.category:
        related_tours = related_tours.filter(category=tour.category)[:4]
    elif tour.destination_region:
        related_tours = related_tours.filter(destination_region=tour.destination_region)[:4]
    else:
        related_tours = related_tours[:4]

    # Handle booking form
    booking_form = None
    booking_success = False
    booking_error = None

    if request.method == 'POST' and request.POST.get('action') == 'book_tour':
        # Handle guest booking or authenticated booking
        user = request.user
        
        if not user.is_authenticated:
            contact_email = request.POST.get('contact_email')
            contact_name = request.POST.get('contact_name')
            
            if contact_email:
                # Check if user exists
                user_exists = User.objects.filter(email=contact_email).exists()
                
                if user_exists:
                    user = User.objects.get(email=contact_email)
                else:
                    # Create new user
                    password =  get_random_string(length=10)
                    username = contact_email  # Use email as username
                    
                    try:
                        user = User.objects.create_user(
                            username=username,
                            email=contact_email,
                            password=password,
                            first_name=contact_name or 'Guest'
                        )
                        
                        # Send email with password
                        subject = 'Your Account for Copenhagen Memories'
                        message = f"""
                        Welcome to Copenhagen Memories!
                        
                        An account has been created for you to manage your booking.
                        
                        Username: {contact_email}
                        Password: {password}
                        
                        You can log in at: {request.build_absolute_uri('/accounts/login/')}
                        """
                        try:
                            send_mail(
                                subject,
                                message,
                                settings.DEFAULT_FROM_EMAIL,
                                [contact_email],
                                fail_silently=True,
                            )
                        except Exception as e:
                            print(e)
                            
                    except Exception as e:
                        booking_error = f"Error creating account: {str(e)}"
                        user = None

        if booking_error is None:
            if not user or (not user.is_authenticated and not contact_email):
                 booking_error = "Please provide an email address to book."
            else:
                try:
                    # Get or create customer
                    customer, created = Customer.objects.get_or_create(
                        user=user,
                        defaults={
                            'phone': request.POST.get('contact_phone', ''),
                        }
                    )

                    # Ensure tour is in POST data
                    post_data = request.POST.copy()
                    post_data['tour'] = str(tour.id)
                    
                    
                    booking_form = FrontendBookingForm(post_data, tour=tour, user=user)
                    participants_data = request.POST.get('participants_data')

                    # Debug form errors
                    if not booking_form.is_valid():
                        print(f"Form errors: {booking_form.errors}")
                        print(f"Participants data: {participants_data}")

                    participants_data = request.POST.get('participants_data')

                    # Only proceed if form is valid and we have participants data
                    if booking_form.is_valid() and participants_data:
                        participants = json.loads(participants_data)

                        # Calculate pricing
                        subtotal = Decimal('0.00')
                        participant_details = []

                        for participant in participants:
                            participant_type = participant.get('type', 'adult')
                            age = participant.get('age')

                            # Find appropriate pricing
                            pricing = None
                            if age is not None:
                                pricing = tour.pricing_options.filter(
                                    is_active=True,
                                    min_age__lte=age,
                                    max_age__gte=age
                                ).first()

                            if not pricing:
                                # Default pricing based on participant type
                                if participant_type == 'adult':
                                    pricing = tour.pricing_options.filter(
                                        participant_type='adult',
                                        is_active=True
                                    ).first()
                                elif participant_type == 'child':
                                    pricing = tour.pricing_options.filter(
                                        participant_type='child',
                                        is_active=True
                                    ).first()
                                else:
                                    pricing = tour.pricing_options.filter(
                                        participant_type='infant',
                                        is_active=True
                                    ).first()

                            if not pricing:
                                # Fallback to base price
                                price = tour.base_price
                            else:
                                price = pricing.price

                            participant['price'] = str(price)
                            subtotal += price
                            participant_details.append(participant)

                        # Handle coupon discount
                        discount_amount = Decimal('0.00')
                        coupon_code = booking_form.cleaned_data.get('coupon_code')
                        applied_coupon = None
                        if coupon_code:
                            try:
                                applied_coupon = Coupon.objects.get(
                                    code=coupon_code.upper(),
                                    is_active=True,
                                    valid_from__lte=timezone.now(),
                                    valid_until__gte=timezone.now()
                                )
                                # Apply coupon logic here
                                if applied_coupon.discount_type == 'percentage':
                                    discount_amount = subtotal * (applied_coupon.discount_value / 100)
                                    if applied_coupon.max_discount_amount and discount_amount > applied_coupon.max_discount_amount:
                                        discount_amount = applied_coupon.max_discount_amount
                                else:  # fixed amount
                                    discount_amount = min(applied_coupon.discount_value, subtotal)
                            except Coupon.DoesNotExist:
                                pass

                        # Calculate tax (assuming 25% VAT for Denmark)
                        # tax_rate = Decimal('0.25')
                        tax_rate = Decimal('0.00')
                        tax_amount = (subtotal - discount_amount) * tax_rate
                        total_amount = subtotal - discount_amount + tax_amount

                        # Generate booking number
                        while True:
                            booking_number = 'BK' + ''.join(random.choices(string.digits, k=8))
                            if not Booking.objects.filter(booking_number=booking_number).exists():
                                break

                        # Create booking
                        booking = Booking.objects.create(
                            booking_number=booking_number,
                            customer=customer,
                            tour=tour,
                            schedule=booking_form.cleaned_data.get('schedule'),
                            tour_date=booking_form.cleaned_data['tour_date'],
                            tour_time=booking_form.cleaned_data.get('tour_time'),
                            tour_time_slot=booking_form.cleaned_data.get('tour_time_slot'),
                            total_participants=len(participants),
                            participant_details=participant_details,
                            subtotal=subtotal,
                            discount_amount=discount_amount,
                            coupon=applied_coupon,
                            tax_amount=tax_amount,
                            total_amount=total_amount,
                            currency=tour.currency,
                            contact_name=booking_form.cleaned_data['contact_name'],
                            contact_email=booking_form.cleaned_data['contact_email'],
                            contact_phone=booking_form.cleaned_data['contact_phone'],
                            special_requirements=booking_form.cleaned_data.get('special_requirements', ''),
                            pickup_location=booking_form.cleaned_data.get('pickup_location', ''),
                            customer_notes=booking_form.cleaned_data.get('customer_notes', ''),
                            status='pending',
                            payment_status='pending',
                            country=booking_form.cleaned_data.get('country', ''),
                        )

                        # Create CouponUsage record if a coupon was used
                        if applied_coupon:
                            from accounts.models import CouponUsage
                            CouponUsage.objects.create(
                                coupon=applied_coupon,
                                customer=customer,
                                booking=booking,
                                discount_amount=discount_amount
                            )
                            # Increment used_count on the coupon
                            applied_coupon.used_count += 1
                            applied_coupon.save()

                        # Create participants
                        for participant in participants:
                            BookingParticipant.objects.create(
                                booking=booking,
                                participant_type=participant.get('type', 'adult'),
                                first_name=participant.get('first_name', ''),
                                last_name=participant.get('last_name', ''),
                                age=participant.get('age'),
                                email=participant.get('email', ''),
                                phone=participant.get('phone', ''),
                                special_requirements=participant.get('special_requirements', ''),
                                price=Decimal(participant.get('price', '0'))
                            )

                        if getattr(settings, 'USE_PAYMENT_GATEWAY', False):
                            import requests
                            from django.urls import reverse
                            
                            api_key = getattr(settings, 'FLATPAY_KEY', '')
                            url = 'https://checkout-api.frisbii.com/v1/session/charge'
                            
                            amount = int(float(total_amount) * 100)
                            accept_url = request.build_absolute_uri(reverse('tour_payment_accept', args=[booking_number]))
                            cancel_url = request.build_absolute_uri(reverse('tour_payment_cancel', args=[booking_number]))
                            
                            data = {
                                'order': {
                                    'handle': booking_number,
                                    'amount': amount,
                                    'currency': 'USD',
                                    'customer': {
                                        'email': booking_form.cleaned_data['contact_email'],
                                        'first_name': booking_form.cleaned_data['contact_name'].split()[0],
                                        'last_name': ' '.join(booking_form.cleaned_data['contact_name'].split()[1:]) if len(booking_form.cleaned_data['contact_name'].split()) > 1 else 'Guest',
                                    }
                                },
                                'accept_url': accept_url,
                                'cancel_url': cancel_url
                            }
                            
                            try:
                                response = requests.post(url, auth=(api_key, ''), json=data)
                                response_data = response.json()
                                if 'url' in response_data:
                                    return redirect(response_data['url'])
                                else:
                                    messages.error(request, f"Payment gateway error: {response_data.get('error', 'Unknown error')}")
                                    return redirect('booking_confirmation', booking_number=booking_number)
                            except Exception as e:
                                messages.error(request, f"Payment gateway error: {str(e)}")
                                return redirect('booking_confirmation', booking_number=booking_number)
                        else:
                            booking_success = True
                            messages.success(request, f'Booking {booking_number} created successfully!')

                            # Redirect to booking confirmation page
                            return redirect('booking_confirmation', booking_number=booking.booking_number)

                    else:
                        booking_error = "Please correct the errors below."

                except Exception as e:
                    booking_error = f"An error occurred: {str(e)}"
                    print(f"Booking error: {str(e)}")  # For debugging

    # Initialize form for GET requests
    if not booking_form:
        booking_form = FrontendBookingForm(tour=tour, user=request.user)

        # Pre-fill user data if authenticated
        if request.user.is_authenticated:
            booking_form.fields['contact_name'].initial = f"{request.user.first_name} {request.user.last_name}".strip()
            booking_form.fields['contact_email'].initial = request.user.email

    # Get pricing options as JSON for JavaScript
    pricing_options = tour.pricing_options.filter(is_active=True).values(
        'participant_type', 'min_age', 'max_age', 'price', 'currency'
    )

    # Convert Decimal objects to floats for JavaScript
    pricing_options_json = []
    for option in pricing_options:
        pricing_options_json.append({
            'participant_type': option['participant_type'],
            'min_age': option['min_age'],
            'max_age': option['max_age'],
            'price': float(option['price']) if option['price'] else 0.0,
            'currency': option['currency']
        })

    # Ensure pricing_options_json is always available (even if empty)
    if not pricing_options_json:
        pricing_options_json = []
    
    # Convert to JSON string for template
    pricing_options_json = json.dumps(pricing_options_json)

    # Get non-form errors if form exists and has been validated
    non_form_errors = []
    if booking_form:
        try:
            # Try to get non-form errors from the form
            if hasattr(booking_form, 'non_form_errors'):
                non_form_errors = list(booking_form.non_form_errors())
            # Also check if there are any __all__ errors in form.errors
            if '__all__' in booking_form.errors:
                non_form_errors.extend(booking_form.errors['__all__'])
        except Exception as e:
            print(f"Error getting non-form errors: {e}")
            non_form_errors = []

    # Handle review submission
    review_form = None
    if request.method == 'POST' and request.POST.get('action') == 'submit_review':
        from .forms import TourReviewForm
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to submit a review.")
        else:
            review_form = TourReviewForm(request.POST)
            if review_form.is_valid():
                customer, created = Customer.objects.get_or_create(user=request.user)
                review = review_form.save(commit=False)
                review.tour = tour
                review.customer = customer
                
                # Check for verified booking
                verified_booking = Booking.objects.filter(
                    customer=customer, 
                    tour=tour, 
                    status='completed'
                ).first()
                if verified_booking:
                    review.verified_booking = True
                    review.booking = verified_booking

                review.save()
                messages.success(request, "Your review has been submitted successfully!")
                return redirect('tour_detail', tour_id=tour.id)
            else:
                messages.error(request, f"There was an error with your review: {review_form.errors}")

    if not review_form:
        from .forms import TourReviewForm
        review_form = TourReviewForm()

    # Get reviews and calculate stats
    from django.db.models import Avg, Count
    reviews = tour.reviews.filter(status='approved').order_by('-created_at')
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0.0
    
    rating_stats = {}
    if total_reviews > 0:
        from django.db.models import Count
        rating_counts = reviews.values('overall_rating').annotate(count=Count('overall_rating'))
        rating_map = {item['overall_rating']: item['count'] for item in rating_counts}
        
        for i in range(5, 0, -1):
            count = rating_map.get(i, 0)
            percentage = (count / total_reviews) * 100
            rating_stats[i] = {
                'count': count,
                'percentage': percentage
            }
    else:
        for i in range(5, 0, -1):
            rating_stats[i] = {'count': 0, 'percentage': 0}

    context = {
        'tour': tour,
        'related_tours': related_tours,
        'images': tour.images.all().order_by('display_order'),
        'highlights': tour.highlights.all().order_by('display_order'),
        'included_items': tour.included_items.all().order_by('display_order'),
        'excluded_items': tour.excluded_items.all().order_by('display_order'),
        'itinerary_steps': tour.itinerary_steps.all().order_by('step_number'),
        'requirements': tour.requirements.all().order_by('display_order'),
        'faqs': tour.faqs.all().order_by('display_order'),
        'pricing_options': tour.pricing_options.filter(is_active=True),
        'pricing_options_json': pricing_options_json,
        'schedules': tour.schedules.filter(status='available').order_by('date', 'start_time')[:10],
        'booking_form': booking_form,
        'booking_success': booking_success,
        'booking_error': booking_error,
        'non_form_errors': non_form_errors,
        'reviews': reviews,
        'rating_stats': rating_stats,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'review_form': review_form,
    }

    return render(request, 'frontend/pages/tour/tour_detail.html', context)


def booking_confirmation(request, booking_number):
    """Booking confirmation page"""
    from accounts.models import Booking

    # Get booking with related data
    booking = get_object_or_404(
        Booking.objects.select_related(
            'customer__user', 'tour__supplier', 'tour__category', 'tour__destination_region', 'tour__city', 'schedule'
        ).prefetch_related('participants'),
        booking_number=booking_number
    )

    # Check if user has permission to view this booking
    # if not request.user.is_authenticated or booking.customer.user != request.user:
    #     messages.error(request, "You don't have permission to view this booking.")
    #     return redirect('home')

    # For guest booking support, we allow public access to confirmation page
    # In a production environment, you might want to add a unique hash to the URL for better security
    
    context = {
        'booking': booking,
        'participants': booking.participants.all(),
    }

    return render(request, 'frontend/pages/booking/confirmation.html', context)


def system_developer(request):
    context = {
        'developer': 'Baizid MD Ashadzzaman',
        'developer_mail': 'baizid.md.ashadzzaman@gmail.com',
        'developer_phone': '8801862420119',
    }
    return render(request, 'frontend/pages/page/system-developer.html', context)


def tour_feature_section(request, feature_id):
    feature_section = get_object_or_404(FeatureSection, pk=feature_id, status='active')
    
    # Get all tours related to this feature section
    tours_list = Tour.objects.filter(
        featuresectiontour__feature_section=feature_section,
        status='active'
    ).select_related(
        'city', 'city__country', 'destination_region'
    ).annotate(
        calculated_average_rating=Coalesce(Avg('reviews__overall_rating'), Value(0.0)),
        calculated_total_reviews=Count('reviews')
    ).prefetch_related(
        'images'
    ).order_by('-created_at')

    paginator = Paginator(tours_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    wishlisted_tours = []
    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        from accounts.models import Wishlist
        wishlisted_tours = list(Wishlist.objects.filter(customer=request.user.customer_profile).values_list('tour_id', flat=True))

    context = {
        'feature_section': feature_section,
        'page_obj': page_obj,
        'wishlisted_tours': wishlisted_tours,
    }
    return render(request, 'frontend/pages/tour/tour_feature_section.html', context) 

def testimonial(request):
    from accounts.models import CustomerReviewStatic, TourReview
    from django.core.paginator import Paginator
    from itertools import chain

    # Fetch reviews
    static_reviews = CustomerReviewStatic.objects.filter(is_active=True).order_by('-created_at')
    tour_reviews = TourReview.objects.filter(status='approved').select_related('customer__user').order_by('-created_at')
    
    combined_reviews = list(chain(static_reviews, tour_reviews))
    
    # Pagination
    paginator = Paginator(combined_reviews, 9) # Show 9 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'frontend/pages/testimonial/testimonial.html', context)

def tour_payment_accept(request, booking_number):
    from accounts.models import Booking
    from django.contrib import messages
    import requests
    
    booking = get_object_or_404(Booking, booking_number=booking_number)
    
    if getattr(settings, 'USE_PAYMENT_GATEWAY', False):
        api_key = getattr(settings, 'FLATPAY_KEY', '')
        url = f"https://api.frisbii.com/v1/charge/{booking_number}"
        try:
            response = requests.get(url, auth=(api_key, ''), headers={'Accept': 'application/json'})
            data = response.json()
            if response.status_code == 200 and data.get('state') not in ['authorized', 'settled']:
                messages.error(request, "Payment was not authorized.")
                return redirect('tour_detail', tour_id=booking.tour.id)
        except Exception as e:
            logger.exception("Payment API failed")
            
    if booking.payment_status != 'paid':
        booking.payment_status = 'paid'
        booking.status = 'confirmed'
        booking.save()

    # Send email to customer
    message = f"""
     Dear {booking.contact_name},
     
     Thank you for your booking with Copenhagen Memories. Here is your booking receipt.
     
     Please arrive 10–15 minutes before your tour starts so we can begin on time. As our tours are carefully scheduled, late arrival may affect your experience.
     
     For walking and bike tours, we recommend wearing comfortable shoes and weather-appropriate clothing. Copenhagen weather can change quickly, so bringing an extra layer or rain jacket is always a good idea. Please also inform the rest of your group.
     
     Meeting information:
     Meeting point: {booking.tour.meeting_point}
     
     If you need help finding us, please contact us before the tour starts at +4566772790.
     
     Booking Receipt:
     Booking Number: {booking.booking_number}
     Tour Name: {booking.tour.title}
     Date: {booking.tour_date}
     Time: {booking.tour_time_slot if booking.tour_time_slot else booking.tour_time}
     Participants: {booking.total_participants}
     Total Amount: {booking.total_amount} USD
    """   

    if booking.contact_email:
        try:
            send_mail(
                'Tour Booking Confirmation',
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.contact_email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Customer email failed: {str(e)}")
    try:
        send_mail(
            'New Tour Booking',
            f'Booking Number: {booking.booking_number}',
            settings.DEFAULT_FROM_EMAIL,
            ['contact@copenhagenmemories.com'],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Admin email failed: {str(e)}")
        
    messages.success(request, f'Payment successful! Your tour booking confirmed. Booking Number: {booking.booking_number}')
    return redirect('booking_confirmation', booking_number=booking.booking_number)

def tour_payment_cancel(request, booking_number):
    from accounts.models import Booking
    from django.contrib import messages
    
    booking = get_object_or_404(Booking, booking_number=booking_number)
    if booking.payment_status != 'paid':
        booking.payment_status = 'failed'
        booking.status = 'cancelled'
        booking.save()
        
    messages.warning(request, "Payment was cancelled.")
    return redirect('tour_detail', tour_id=booking.tour.id)