from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from accounts.models import Bike, BikeAddon, BikeAddonPrice, BikeBooking, BikeBookingAddon, Customer
from .forms import BikeBookingForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_bikebooking')
def bike_booking_list(request):
    search_query = request.GET.get('search', '')
    bookings = BikeBooking.objects.all()
    
    if search_query:
        bookings = bookings.filter(
            Q(booking_number__icontains=search_query) | 
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/bike_bookings/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_bikebooking')
def bike_booking_create(request):
    if request.method == 'POST':
        form = BikeBookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            
            # Handle selected addons
            addon_ids = request.POST.getlist('selected_addons')
            for addon_id in addon_ids:
                try:
                    addon = BikeAddon.objects.get(id=addon_id)
                    bike_addon_price = BikeAddonPrice.objects.filter(bike=booking.bike, addon=addon).first()
                    price = bike_addon_price.price if bike_addon_price else 0
                    
                    # Get quantity from POST data
                    quantity = request.POST.get(f'addon_quantity_{addon_id}', 1)
                    try:
                        quantity = int(quantity)
                    except (ValueError, TypeError):
                        quantity = 1
                    
                    BikeBookingAddon.objects.create(
                        booking=booking,
                        addon=addon,
                        price=price,
                        quantity=quantity
                    )
                except Exception as e:
                    print(f"Error adding addon {addon_id} to booking: {e}")
            
            messages.success(request, 'Bike booking created successfully!')
            return redirect('bike_booking_list')
    else:
        form = BikeBookingForm()
    
    customers = Customer.objects.all()
    bikes = Bike.objects.all()
    
    return render(request, 'accounts/admin/bike_bookings/create.html', {
        'form': form,
        'customers': customers,
        'bikes': bikes
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_bikebooking')
def bike_booking_edit(request, pk):
    booking = get_object_or_404(BikeBooking, pk=pk)
    
    if request.method == 'POST':
        form = BikeBookingForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save()
            
            # Update addons
            booking.booking_addons.all().delete()
            addon_ids = request.POST.getlist('selected_addons')
            for addon_id in addon_ids:
                try:
                    addon = BikeAddon.objects.get(id=addon_id)
                    bike_addon_price = BikeAddonPrice.objects.filter(bike=booking.bike, addon=addon).first()
                    price = bike_addon_price.price if bike_addon_price else 0
                    
                    # Get quantity from POST data
                    quantity = request.POST.get(f'addon_quantity_{addon_id}', 1)
                    try:
                        quantity = int(quantity)
                    except (ValueError, TypeError):
                        quantity = 1
                    
                    BikeBookingAddon.objects.create(
                        booking=booking,
                        addon=addon,
                        price=price,
                        quantity=quantity
                    )
                except Exception as e:
                    print(f"Error updating addon {addon_id}: {e}")
            
            messages.success(request, 'Bike booking updated successfully!')
            return redirect('bike_booking_list')
    else:
        form = BikeBookingForm(instance=booking)
    
    customers = Customer.objects.all()
    bikes = Bike.objects.all()
    current_selected_addon_ids = list(booking.booking_addons.values_list('addon_id', flat=True))
    
    # We also need the addons for the CURRENTLY selected bike to show in the list
    bike_addons = BikeAddonPrice.objects.filter(bike=booking.bike)
    
    # Get current addon quantities for the template
    addon_quantities = {ab.addon_id: ab.quantity for ab in booking.booking_addons.all()}
    
    return render(request, 'accounts/admin/bike_bookings/edit.html', {
        'form': form,
        'booking': booking,
        'customers': customers,
        'bikes': bikes,
        'bike_addons': bike_addons,
        'current_selected_addon_ids': current_selected_addon_ids,
        'addon_quantities': addon_quantities
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_bikebooking')
def bike_booking_delete(request, pk):
    booking = get_object_or_404(BikeBooking, pk=pk)
    booking.delete()
    messages.success(request, 'Bike booking deleted successfully!')
    return redirect('bike_booking_list')

@login_required
@user_passes_test(lambda u: u.is_staff)
def get_bike_addons_api(request, bike_id):
    bike = get_object_or_404(Bike, id=bike_id)
    addons = BikeAddonPrice.objects.filter(bike=bike).select_related('addon')
    
    data = []
    for ba in addons:
        data.append({
            'id': ba.addon.id,
            'title': ba.addon.title,
            'price': float(ba.price)
        })
    
    return JsonResponse({
        'bike_price': float(bike.price),
        'addons': data
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def get_customer_info_api(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    return JsonResponse({
        'name': f"{customer.user.first_name} {customer.user.last_name}",
        'email': customer.user.email,
        'phone': customer.phone,
        'address': customer.address
    })
