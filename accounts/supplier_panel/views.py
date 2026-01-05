from django.shortcuts import render, redirect
from accounts.forms import TourSupplierRegistrationForm, TourSupplierLoginForm
from django.contrib import messages
from accounts.models import TourSupplier,Tour,Booking,Payment


def supplier_profile(request):
    supplier_id = request.session.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Please login first.')
        return redirect('login_tour_supplier')
    
    supplier = TourSupplier.objects.get(id=supplier_id)
    
    if request.method == 'POST':
        supplier.name = request.POST.get('name')
        supplier.email = request.POST.get('email')
        supplier.phone = request.POST.get('phone')
        supplier.address = request.POST.get('address')
        supplier.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('supplier_profile')
        
    return render(request, 'accounts/tour_supplier/pages/supplier_profile.html', {'supplier': supplier})

def supplier_tours(request):
    supplier_id = request.session.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Please login first.')
        return redirect('login_tour_supplier')
    
    supplier = TourSupplier.objects.get(id=supplier_id)
    tours = Tour.objects.filter(supplier=supplier)
    return render(request, 'accounts/tour_supplier/pages/supplier_tours.html', {'supplier': supplier, 'tours': tours})

def supplier_tour_view(request, tour_id):
    tour = Tour.objects.get(id=tour_id)
    return render(request, 'accounts/tour_supplier/pages/supplier_tour_view.html', {'tour': tour})

def supplier_bookings(request):
    supplier_id = request.session.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Please login first.')
        return redirect('login_tour_supplier')
    
    supplier = TourSupplier.objects.get(id=supplier_id)
    bookings = Booking.objects.filter(tour__supplier=supplier)
    return render(request, 'accounts/tour_supplier/pages/supplier_booking.html', {'supplier': supplier, 'bookings': bookings})


def supplier_payments(request):
    supplier_id = request.session.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Please login first.')
        return redirect('login_tour_supplier')
    
    supplier = TourSupplier.objects.get(id=supplier_id)
    payments = Payment.objects.filter(booking__tour__supplier=supplier)
    return render(request, 'accounts/tour_supplier/pages/supplier_payments.html', {'supplier': supplier, 'payments': payments})


def supplier_dashboard(request):
    supplier_id = request.session.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Please login first.')
        return redirect('login_tour_supplier')
    
    supplier = TourSupplier.objects.get(id=supplier_id)
    return render(request, 'accounts/tour_supplier/dashboard.html', {'supplier': supplier})


def register_tour_supplier(request):
    if request.method == 'POST':
        form = TourSupplierRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tour Supplier registration successful! You can now login.')
            return redirect('login_tour_supplier')
    else:
        form = TourSupplierRegistrationForm()
    
    return render(request, 'accounts/tour_supplier/register.html', {'form': form}) 

def login_tour_supplier(request):
    if request.method == 'POST':
        form = TourSupplierLoginForm(request.POST)
        if form.is_valid():
            supplier = form.cleaned_data['supplier']
            # Manually storing supplier ID in session as this is a custom login
            request.session['supplier_id'] = supplier.id
            messages.success(request, 'Successfully logged in!')
            return redirect('tour_supplier_dashboard')
    else:
        form = TourSupplierLoginForm()
    
    return render(request, 'accounts/tour_supplier/login.html', {'form': form})

def tour_supplier_dashboard(request):
    supplier_id = request.session.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Please login first.')
        return redirect('login_tour_supplier')
    
    supplier = TourSupplier.objects.get(id=supplier_id)
    
    # Calculate stats
    total_tours = Tour.objects.filter(supplier=supplier).count()
    total_bookings = Booking.objects.filter(tour__supplier=supplier).count()
    
    # Recent bookings (e.g., last 5)
    recent_bookings = Booking.objects.filter(
        tour__supplier=supplier
    ).select_related('tour', 'customer').order_by('-created_at')[:5]
    
    context = {
        'supplier': supplier,
        'total_tours': total_tours,
        'total_bookings': total_bookings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'accounts/tour_supplier/dashboard.html', context)

def logout_tour_supplier(request):
    if 'supplier_id' in request.session:
        del request.session['supplier_id']
    messages.success(request, 'Successfully logged out!')
    return redirect('login_tour_supplier')