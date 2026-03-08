from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from accounts.models import Booking, BookingParticipant, Tour, Customer, TourSchedule, TourPricing
from .decorators import permission_required_with_message
from .forms_additions import BookingForm

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_booking')
def booking_list(request):
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    payment_status = request.GET.get('payment_status', '')
    
    bookings = Booking.objects.select_related('customer__user', 'tour').all().order_by('-created_at')
    
    if search_query:
        bookings = bookings.filter(
            Q(booking_number__icontains=search_query) |
            Q(contact_name__icontains=search_query) |
            Q(contact_email__icontains=search_query)
        )
    
    if status:
        bookings = bookings.filter(status=status)
    if payment_status:
        bookings = bookings.filter(payment_status=payment_status)
    
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/bookings/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status': status,
        'payment_status': payment_status,
        'status_choices': Booking._meta.get_field('status').choices,
        'payment_status_choices': Booking._meta.get_field('payment_status').choices
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_booking')
def booking_detail(request, pk):
    booking = get_object_or_404(Booking.objects.select_related('customer__user', 'tour', 'schedule'), pk=pk)
    participants = booking.participants.all() if hasattr(booking, 'participants') else []
    return render(request, 'accounts/admin/bookings/detail.html', {
        'booking': booking,
        'participants': participants
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_booking')
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            messages.success(request, 'Booking created successfully!')
            return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingForm()
    
    return render(request, 'accounts/admin/bookings/create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_booking')
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    participants = booking.participants.all() if hasattr(booking, 'participants') else []
    
    # Pre-populate participants for the dynamic JS list
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    participants_list = []
    for p in participants:
        participants_list.append({
            'participant_type': p.participant_type,
            'first_name': p.first_name,
            'last_name': p.last_name,
            'age': p.age,
            'email': p.email,
            'phone': p.phone,
            'special_requirements': p.special_requirements,
            'price': float(p.price)
        })
    participants_json = json.dumps(participants_list, cls=DjangoJSONEncoder)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save()
            # Note: The BookingForm.save() should ideally handle participants_data from request.POST
            messages.success(request, 'Booking updated successfully!')
            return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingForm(instance=booking)
    
    return render(request, 'accounts/admin/bookings/edit.html', {
        'form': form, 
        'booking': booking,
        'participants_json': participants_json
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_booking')
def booking_status_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Booking._meta.get_field('status').choices):
            booking.status = status
            booking.save()
            messages.success(request, f'Booking status updated to {status}!')
        return redirect('booking_detail', pk=booking.pk)
    return redirect('booking_detail', pk=booking.pk)

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_booking')
def booking_participants_list(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    participants = booking.participants.all() if hasattr(booking, 'participants') else []
    return render(request, 'accounts/admin/bookings/participants_list.html', {
        'booking': booking,
        'participants': participants
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_booking')
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    booking.delete()
    messages.success(request, 'Booking deleted successfully!')
    return redirect('booking_list')

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_booking')
def booking_invoice(request, pk):
    booking = get_object_or_404(Booking.objects.select_related('customer__user', 'tour'), pk=pk)
    participants = booking.participants.all() if hasattr(booking, 'participants') else []
    return render(request, 'accounts/admin/bookings/invoice.html', {
        'booking': booking,
        'participants': participants
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_booking')
def booking_add_payment(request, pk):
    # This is a placeholder for adding payment logic
    return redirect('booking_detail', pk=pk)

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_booking')
def booking_send_invoice(request, pk):
    # This is a placeholder for sending invoice via email
    messages.success(request, 'Invoice sent successfully!')
    return redirect('booking_detail', pk=pk)
@login_required
@user_passes_test(lambda u: u.is_staff)
def get_tour_pricing_api(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    pricing_options = TourPricing.objects.filter(tour=tour, is_active=True)
    
    pricing_data = []
    if pricing_options.exists():
        for pricing in pricing_options:
            pricing_data.append({
                'type': pricing.participant_type,
                'price': float(pricing.price),
                'description': pricing.description
            })
    else:
        # Fallback to base_price if no specific pricing options are defined
        pricing_data.append({
            'type': 'adult',
            'price': float(tour.base_price),
            'description': 'Base Price'
        })
    
    return JsonResponse({
        'base_price': float(tour.base_price),
        'pricing': pricing_data
    })
