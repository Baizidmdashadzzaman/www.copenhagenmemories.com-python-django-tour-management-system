from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.forms import AdminRegistrationForm, LoginForm
from django.contrib import messages

# Import separated views
from .views_destination import (
    destination_region_list,
    destination_region_create,
    destination_region_edit,
    destination_region_delete
)
from .views_country import (
    country_list,
    country_create,
    country_edit,
    country_delete
)
from .views_customer import (
    customer_list,
    customer_create,
    customer_edit,
    customer_delete,
    customer_booking_list,
    customer_wishlist
)
from .views_settings import site_settings
from .views_contactus import (
    contactus_list,
    contactus_create,
    contactus_edit,
    contactus_delete
)
from .views_tours import (
    tour_list,
    tour_create,
    tour_edit,
    tour_delete,
    tour_image_list,
    tour_highlights_list
)
from .views_bookings import (
    booking_list,
    booking_detail,
    booking_status_update,
    booking_participants_list,
    booking_create,
    booking_edit
)
from .views_payments import (
    payment_list,
    payment_detail,
    payment_status_update
)
from .views_reviews import (
    review_list,
    review_create,
    review_edit,
    review_delete,
    tour_review_list,
    tour_review_detail,
    tour_review_status_update,
    tour_review_feature_toggle
)
from .views_coupons import (
    coupon_list,
    coupon_detail,
    coupon_toggle_active
)
from .views_cities import (
    city_list,
    city_detail,
    city_toggle_active,
    city_toggle_popular
)
from .views_blog import (
    blog_list,
    blog_detail,
    blog_status_update,
    blog_feature_toggle
)
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Access denied. This portal is for administrators only.")
    else:
        form = LoginForm()
    return render(request, 'accounts/admin/login.html', {'form': form})

def register_admin(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('admin_dashboard')
    else:
        form = AdminRegistrationForm()
    return render(request, 'accounts/admin/register.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    from accounts.models import (
        Booking, Payment, Tour, Customer, TourReview, 
        Coupon, City, BlogPost
    )
    from django.db.models import Sum, Count, Q, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    # Date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Booking Statistics
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    cancelled_bookings = Booking.objects.filter(status='cancelled').count()
    bookings_this_month = Booking.objects.filter(created_at__gte=last_30_days).count()
    
    # Revenue Statistics
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    revenue_this_month = Payment.objects.filter(
        status='completed',
        created_at__gte=last_30_days
    ).aggregate(total=Sum('amount'))['total'] or 0
    pending_payments = Payment.objects.filter(status='pending').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Tour Statistics
    total_tours = Tour.objects.count()
    active_tours = Tour.objects.filter(status='active').count()
    draft_tours = Tour.objects.filter(status='draft').count()
    
    # Customer Statistics
    total_customers = Customer.objects.count()
    new_customers_this_month = Customer.objects.filter(
        created_at__gte=last_30_days
    ).count()
    
    # Review Statistics
    total_reviews = TourReview.objects.count()
    pending_reviews = TourReview.objects.filter(status='pending').count()
    approved_reviews = TourReview.objects.filter(status='approved').count()
    average_rating = TourReview.objects.filter(
        status='approved'
    ).aggregate(avg=Avg('overall_rating'))['avg'] or 0
    
    # Recent Bookings (last 10)
    recent_bookings = Booking.objects.select_related(
        'customer__user', 'tour'
    ).order_by('-created_at')[:10]
    
    # Recent Reviews (last 5)
    recent_reviews = TourReview.objects.select_related(
        'customer__user', 'tour'
    ).order_by('-created_at')[:5]
    
    # Top Tours by Bookings
    top_tours = Tour.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:5]
    
    # Monthly booking data for chart (last 6 months)
    monthly_bookings = []
    monthly_revenue = []
    for i in range(5, -1, -1):
        month_start = today - timedelta(days=30*i)
        month_end = today - timedelta(days=30*(i-1)) if i > 0 else today
        
        bookings = Booking.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        revenue = Payment.objects.filter(
            status='completed',
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_bookings.append(bookings)
        monthly_revenue.append(float(revenue))
    
    # Booking status distribution
    booking_status_data = {
        'pending': pending_bookings,
        'confirmed': confirmed_bookings,
        'cancelled': cancelled_bookings,
    }
    
    context = {
        # Summary stats
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'bookings_this_month': bookings_this_month,
        'total_revenue': total_revenue,
        'revenue_this_month': revenue_this_month,
        'pending_payments': pending_payments,
        'total_tours': total_tours,
        'active_tours': active_tours,
        'draft_tours': draft_tours,
        'total_customers': total_customers,
        'new_customers_this_month': new_customers_this_month,
        'total_reviews': total_reviews,
        'pending_reviews': pending_reviews,
        'approved_reviews': approved_reviews,
        'average_rating': round(average_rating, 1),
        
        # Lists
        'recent_bookings': recent_bookings,
        'recent_reviews': recent_reviews,
        'top_tours': top_tours,
        
        # Chart data
        'monthly_bookings': monthly_bookings,
        'monthly_revenue': monthly_revenue,
        'booking_status_data': booking_status_data,
    }
    
    return render(request, 'accounts/admin/dashboard.html', context)
