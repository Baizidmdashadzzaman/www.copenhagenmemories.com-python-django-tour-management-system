from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Booking, BookingParticipant
from .decorators import permission_required_with_message
from .forms_additions import BookingForm

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_booking')
def booking_list(request):
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    payment_status = request.GET.get('payment_status', '')
    
    bookings = Booking.objects.select_related('customer', 'tour', 'schedule').all()
    
    if search_query:
        bookings = bookings.filter(
            Q(booking_number__icontains=search_query) |
            Q(customer__user__username__icontains=search_query) |
            Q(contact_email__icontains=search_query) |
            Q(tour__title__icontains=search_query)
        )
    
    if status:
        bookings = bookings.filter(status=status)
    
    if payment_status:
        bookings = bookings.filter(payment_status=payment_status)
    
    bookings = bookings.order_by('-created_at')
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
    participants = booking.participants.all()
    payments = booking.payments.all()
    
    return render(request, 'accounts/admin/bookings/detail.html', {
        'booking': booking,
        'participants': participants,
        'payments': payments
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_booking')
def booking_status_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Booking._meta.get_field('status').choices):
            booking.status = new_status
            booking.save()
            messages.success(request, f'Booking status updated to {new_status}!')
            return redirect('booking_detail', pk=booking.pk)
        else:
            messages.error(request, 'Invalid status!')
    
    return render(request, 'accounts/admin/bookings/status_update.html', {
        'booking': booking,
        'status_choices': Booking._meta.get_field('status').choices
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_bookingparticipant')
def booking_participants_list(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    participants = booking.participants.all()
    
    return render(request, 'accounts/admin/bookings/participants_list.html', {
        'booking': booking,
        'participants': participants
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_booking')
def booking_invoice(request, pk):
    booking = get_object_or_404(Booking.objects.select_related('customer__user', 'tour', 'schedule'), pk=pk)
    participants = booking.participants.all()
    payments = booking.payments.all()
    
    return render(request, 'accounts/admin/bookings/invoice.html', {
        'booking': booking,
        'participants': participants,
        'payments': payments
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_payment')
def booking_add_payment(request, pk):
    from django.http import JsonResponse
    from accounts.models import Payment
    from decimal import Decimal
    from django.utils import timezone
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    
    booking = get_object_or_404(Booking, pk=pk)
    
    try:
        # Get form data
        amount = Decimal(request.POST.get('amount', 0))
        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method')
        payment_note = request.POST.get('payment_note', '')
        
        # Validate amount
        if amount <= 0:
            return JsonResponse({'success': False, 'error': 'Payment amount must be greater than 0'}, status=400)
        
        # Calculate total paid so far
        total_paid = sum(p.amount for p in booking.payments.filter(status='completed'))
        remaining = booking.total_amount - total_paid
        
        if amount > remaining:
            return JsonResponse({
                'success': False, 
                'error': f'Payment amount ({amount} {booking.currency}) exceeds remaining balance ({remaining} {booking.currency})'
            }, status=400)
        
        # Validate payment method
        valid_methods = ['card', 'bank_transfer', 'cash', 'mobile_payment', 'credit_card', 'paypal', 'stripe']
        if payment_method not in valid_methods:
            return JsonResponse({'success': False, 'error': 'Invalid payment method'}, status=400)
        
        # Parse payment date
        if payment_date:
            paid_at = timezone.datetime.strptime(payment_date, '%Y-%m-%d')
            paid_at = timezone.make_aware(paid_at)
        else:
            paid_at = timezone.now()
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            amount=amount,
            currency=booking.currency,
            payment_method=payment_method,
            status='completed',
            paid_at=paid_at,
            gateway_response={'note': payment_note} if payment_note else {}
        )
        
        # Update booking payment status
        new_total_paid = total_paid + amount
        if new_total_paid >= booking.total_amount:
            booking.payment_status = 'paid'
        elif new_total_paid > 0:
            booking.payment_status = 'partial'
        
        booking.save()
        
        messages.success(request, f'Payment of {amount} {booking.currency} added successfully!')
        
        return JsonResponse({
            'success': True,
            'message': f'Payment of {amount} {booking.currency} added successfully!',
            'payment_id': payment.id,
            'new_payment_status': booking.payment_status
        })
        
    except ValueError as e:
        return JsonResponse({'success': False, 'error': f'Invalid data: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'}, status=500)

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_booking')
def booking_send_invoice(request, pk):
    from django.http import JsonResponse
    from django.core.mail import send_mail
    from django.conf import settings
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    
    booking = get_object_or_404(Booking, pk=pk)
    
    try:
        # Get form data
        from_email = request.POST.get('from_email', settings.DEFAULT_FROM_EMAIL)
        to_email = request.POST.get('to_email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Validate email
        if not to_email:
            return JsonResponse({'success': False, 'error': 'Recipient email is required'}, status=400)
        
        if not subject:
            return JsonResponse({'success': False, 'error': 'Email subject is required'}, status=400)
        
        if not message:
            return JsonResponse({'success': False, 'error': 'Email message is required'}, status=400)
        
        # Send email
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False,
            )
            
            messages.success(request, f'Invoice sent successfully to {to_email}!')
            
            return JsonResponse({
                'success': True,
                'message': f'Invoice sent successfully to {to_email}!'
            })
            
        except Exception as email_error:
            # Log the error but return a user-friendly message
            print(f"Email sending error: {str(email_error)}")
            return JsonResponse({
                'success': False, 
                'error': 'Failed to send email. Please check email configuration.'
            }, status=500)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'}, status=500)


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_booking')
def booking_create(request):
    import json
    from decimal import Decimal
    import random
    import string
    from datetime import datetime
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        
        if form.is_valid():
            try:
                # Get participants data from POST
                participants_data = json.loads(request.POST.get('participants_data', '[]'))
                
                if not participants_data:
                    messages.error(request, 'At least one participant is required.')
                    return render(request, 'accounts/admin/bookings/create.html', {'form': form})
                
                # Create booking instance but don't save yet
                booking = form.save(commit=False)
                
                # Generate unique booking number
                while True:
                    booking_number = 'BK' + ''.join(random.choices(string.digits, k=8))
                    if not Booking.objects.filter(booking_number=booking_number).exists():
                        break
                
                booking.booking_number = booking_number
                booking.total_participants = len(participants_data)
                
                # Save the booking
                booking.save()
                
                # Create participants
                for participant_data in participants_data:
                    BookingParticipant.objects.create(
                        booking=booking,
                        participant_type=participant_data.get('type', 'adult'),
                        first_name=participant_data.get('first_name', ''),
                        last_name=participant_data.get('last_name', ''),
                        age=participant_data.get('age') or None,
                        email=participant_data.get('email', ''),
                        phone=participant_data.get('phone', ''),
                        special_requirements=participant_data.get('special_requirements', ''),
                        price=Decimal(participant_data.get('price', '0'))
                    )
                
                messages.success(request, f'Booking {booking.booking_number} created successfully!')
                return redirect('booking_detail', pk=booking.pk)
                
            except json.JSONDecodeError:
                messages.error(request, 'Invalid participant data.')
            except Exception as e:
                messages.error(request, f'Error creating booking: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm()
    
    return render(request, 'accounts/admin/bookings/create.html', {
        'form': form
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_booking')
def booking_edit(request, pk):
    import json
    from decimal import Decimal
    
    booking = get_object_or_404(Booking, pk=pk)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        
        if form.is_valid():
            try:
                # Get participants data from POST
                participants_data = json.loads(request.POST.get('participants_data', '[]'))
                
                if not participants_data:
                    messages.error(request, 'At least one participant is required.')
                    return render(request, 'accounts/admin/bookings/edit.html', {
                        'form': form,
                        'booking': booking
                    })
                
                # Update booking
                booking = form.save(commit=False)
                booking.total_participants = len(participants_data)
                booking.save()
                
                # Delete existing participants and create new ones
                booking.participants.all().delete()
                
                for participant_data in participants_data:
                    BookingParticipant.objects.create(
                        booking=booking,
                        participant_type=participant_data.get('type', 'adult'),
                        first_name=participant_data.get('first_name', ''),
                        last_name=participant_data.get('last_name', ''),
                        age=participant_data.get('age') or None,
                        email=participant_data.get('email', ''),
                        phone=participant_data.get('phone', ''),
                        special_requirements=participant_data.get('special_requirements', ''),
                        price=Decimal(participant_data.get('price', '0'))
                    )
                
                messages.success(request, f'Booking {booking.booking_number} updated successfully!')
                return redirect('booking_detail', pk=booking.pk)
                
            except json.JSONDecodeError:
                messages.error(request, 'Invalid participant data.')
            except Exception as e:
                messages.error(request, f'Error updating booking: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm(instance=booking)
    
    # Get existing participants
    participants = list(booking.participants.values(
        'participant_type', 'first_name', 'last_name', 'age', 
        'email', 'phone', 'special_requirements', 'price'
    ))
    
    # Convert Decimal to string for JSON serialization
    for participant in participants:
        if participant.get('price'):
            participant['price'] = str(participant['price'])
    
    return render(request, 'accounts/admin/bookings/edit.html', {
        'form': form,
        'booking': booking,
        'participants_json': json.dumps(participants)
    })
