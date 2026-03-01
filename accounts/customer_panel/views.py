from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.forms import CustomerRegistrationForm, LoginForm
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_staff:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('customer_dashboard')
            else:
                messages.error(request, "Access denied. Administrators should use the Admin Portal.")
    else:
        form = LoginForm()
    return render(request, 'accounts/customer/login.html', {'form': form})

def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save()
            login(request, customer.user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/customer/register.html', {'form': form})

@login_required
@user_passes_test(lambda u: not u.is_staff)
def customer_dashboard(request):
    from accounts.models import Booking
    from django.db.models import Sum, Avg
    from django.utils import timezone
    
    customer = request.user.customer_profile
    bookings = Booking.objects.filter(customer=customer)
    
    # Statistics
    total_bookings_count = bookings.count()
    
    # Calculate total transactions (sum of paid bookings)
    total_transactions = bookings.filter(payment_status='paid').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Calculate average booking value
    average_value = bookings.aggregate(
        avg=Avg('total_amount')
    )['avg'] or 0
    
    # Recent bookings
    recent_bookings = bookings.order_by('-created_at')[:5]
    
    # Upcoming reminder (next confirmed booking)
    upcoming_reminder = bookings.filter(
        status='confirmed',
        tour_date__gte=timezone.now().date()
    ).order_by('tour_date', 'tour_time').first()
    
    # Recent invoices (paid bookings)
    recent_invoices = bookings.filter(
        payment_status='paid'
    ).order_by('-created_at')[:5]

    # Popular/Featured Tours (Recommendation)
    from accounts.models import Tour, CustomerMessage
    popular_tours = Tour.objects.filter(status='active', is_featured=True).order_by('-average_rating')[:4]
    
    # Recent Messages
    recent_messages = CustomerMessage.objects.filter(customer=customer).order_by('-created_at')[:4]
    
    context = {
        'total_bookings_count': total_bookings_count,
        'total_transactions': total_transactions,
        'average_value': average_value,
        'recent_bookings': recent_bookings,
        'upcoming_reminder': upcoming_reminder,
        'recent_invoices': recent_invoices,
        'popular_tours': popular_tours,
        'recent_messages': recent_messages,
    }
    
    return render(request, 'accounts/customer/dashboard.html', context)

@login_required
@user_passes_test(lambda u: not u.is_staff)
def customer_booking_list(request):
    bookings = request.user.customer_profile.bookings.all().order_by('-created_at')
    return render(request, 'accounts/customer/pages/customer_tour_booking_list.html', {'bookings': bookings})

@login_required
@user_passes_test(lambda u: not u.is_staff)
def customer_booking_detail(request, booking_id):
    from accounts.models import Booking
    from django.shortcuts import get_object_or_404
    
    booking = get_object_or_404(Booking, id=booking_id, customer__user=request.user)
    return render(request, 'accounts/customer/pages/customer_tour_booking_view.html', {'booking': booking})

@login_required
@user_passes_test(lambda u: not u.is_staff)
def customer_profile_update(request):
    from accounts.forms import CustomerProfileUpdateForm
    from django.contrib.auth import update_session_auth_hash
    
    customer = request.user.customer_profile
    if request.method == 'POST':
        form = CustomerProfileUpdateForm(request.POST, request.FILES, instance=customer, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            # Re-login user if password changed to prevent logout
            if form.cleaned_data.get('new_password'):
                update_session_auth_hash(request, request.user)
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('customer_profile')
    else:
        form = CustomerProfileUpdateForm(instance=customer, user=request.user)
    
    return render(request, 'accounts/customer/pages/customer_profile.html', {'form': form})

@login_required
@user_passes_test(lambda u: not u.is_staff)
def customer_messages(request):
    from accounts.models import CustomerMessage
    from accounts.forms import CustomerMessageForm
    
    customer = request.user.customer_profile
    customer_messages = CustomerMessage.objects.filter(customer=customer).order_by('created_at')
    
    if request.method == 'POST':
        form = CustomerMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.customer = customer
            message.sender_type = 'customer'
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('customer_messages')
    else:
        form = CustomerMessageForm()
    
    context = {
        'customer_messages': customer_messages,
        'form': form,
    }
    return render(request, 'accounts/customer/pages/customer_message.html', context)

@login_required
@user_passes_test(lambda u: not u.is_staff)
def customer_reviews(request):
    from accounts.models import TourReview
    
    customer = request.user.customer_profile
    reviews = TourReview.objects.filter(customer=customer).order_by('-created_at')
    
    context = {
        'reviews': reviews,
    }
    return render(request, 'accounts/customer/pages/customer_review.html', context)


@login_required
@user_passes_test(lambda u: not u.is_staff)
def customer_review_delete(request, review_id):
    from accounts.models import TourReview
    from django.contrib import messages
    from django.shortcuts import get_object_or_404, redirect
    
    review = get_object_or_404(TourReview, id=review_id, customer=request.user.customer_profile)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, "Review deleted successfully.")
        
    return redirect('customer_reviews')

@login_required
@user_passes_test(lambda u: not u.is_staff)
def customer_wishlist_page(request):
    from accounts.models import Wishlist
    
    customer = request.user.customer_profile
    wishlist_items = Wishlist.objects.filter(customer=customer).select_related('tour', 'tour__city', 'tour__destination_region').order_by('-created_at')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'accounts/customer/pages/customer_wishlist.html', context)

@login_required
def toggle_wishlist(request):
    from accounts.models import Wishlist, Tour
    from django.http import JsonResponse
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tour_id = data.get('tour_id')
            
            if not tour_id:
                return JsonResponse({'status': 'error', 'message': 'Tour ID is required'}, status=400)
            
            tour = Tour.objects.get(id=tour_id)
            customer = request.user.customer_profile
            
            wishlist_item, created = Wishlist.objects.get_or_create(customer=customer, tour=tour)
            
            if not created:
                # If it already exists, delete it (toggle off)
                wishlist_item.delete()
                return JsonResponse({'status': 'removed', 'message': 'Tour removed from wishlist'})
            else:
                return JsonResponse({'status': 'added', 'message': 'Tour added to wishlist'})
                
        except Tour.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tour not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def get_chat_messages(request):
    from accounts.models import CustomerMessage
    from django.http import JsonResponse
    
    unique_customer_id = request.COOKIES.get('unique_customer_id')
    
    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        customer = request.user.customer_profile
        messages_list = CustomerMessage.objects.filter(customer=customer).order_by('created_at')
    elif unique_customer_id:
        messages_list = CustomerMessage.objects.filter(unique_customer_id=unique_customer_id, customer__isnull=True).order_by('created_at')
    else:
        return JsonResponse({'status': 'success', 'messages': []})
        
    data = []
    for msg in messages_list:
        data.append({
            'message': msg.message,
            'admin_id': msg.sender_admin.id if msg.sender_admin else None,
            'created_at': msg.created_at.isoformat(),
            'file': None 
        })
        
    return JsonResponse({'status': 'success', 'messages': data})

def send_chat_message(request):
    from accounts.models import CustomerMessage
    from django.http import JsonResponse
    
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if not message_text:
            return JsonResponse({'status': 'error', 'message': 'Message is empty'}, status=400)
            
        unique_customer_id = request.COOKIES.get('unique_customer_id')
        
        customer = None
        if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
            customer = request.user.customer_profile
        
        if not customer and not unique_customer_id:
            return JsonResponse({'status': 'error', 'message': 'User session not identified'}, status=400)
            
        CustomerMessage.objects.create(
            customer=customer,
            unique_customer_id=unique_customer_id if not customer else None,
            sender_type='customer',
            subject='Chat Message',
            message=message_text,
            is_read=False
        )
        
        return JsonResponse({'status': 'success'})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

def forget_password(request):
    from django.contrib.auth.models import User
    from django.core.mail import send_mail
    from django.conf import settings
    from django.utils.crypto import get_random_string
    
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.filter(email=email).first()
            
            if user:
                # Generate new password
                new_password = get_random_string(length=10)
                user.set_password(new_password)
                user.save()
                
                # Send email
                site_name = "Your Tour Guide"
                try:
                    from accounts.models import SiteSetting
                    settings_obj = SiteSetting.get_settings()
                    site_name = settings_obj.site_name
                except:
                    pass
                    
                subject = f'Password Reset - {site_name}'
                message = f'Hello {user.username},\n\nYour password has been successfully reset upon your request.\n\nYour new password is: {new_password}\n\nPlease login using this password and change it immediately from your profile settings.\n\nBest regards,\n{site_name} Team'
                email_from = getattr(settings, 'EMAIL_HOST_USER', 'noreply@example.com')
                recipient_list = [user.email]
                
                send_mail(subject, message, email_from, recipient_list)
                
                messages.success(request, 'A new password has been sent to your email address. Please check your inbox.')
                return redirect('login')
            else:
                messages.error(request, 'No account found with this email address.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            
    return render(request, 'accounts/customer/forget-password.html')
