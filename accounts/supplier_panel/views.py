from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from accounts.forms import TourSupplierRegistrationForm, TourSupplierLoginForm, TourSupplierProfileUpdateForm, SupplierTourForm
from django.contrib import messages
from accounts.models import TourSupplier,Tour,Booking,Payment


def supplier_profile(request):
    supplier_id = request.session.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Please login first.')
        return redirect('login_tour_supplier')
    
    supplier = TourSupplier.objects.get(id=supplier_id)
    
    if request.method == 'POST':
        form = TourSupplierProfileUpdateForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('supplier_profile')
    else:
        form = TourSupplierProfileUpdateForm(instance=supplier)
        
    return render(request, 'accounts/tour_supplier/pages/supplier_profile.html', {'supplier': supplier, 'form': form})

def supplier_tours(request):
    supplier_id = request.session.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Please login first.')
        return redirect('login_tour_supplier')
    
    supplier = TourSupplier.objects.get(id=supplier_id)
    
    if request.method == 'POST':
        form = SupplierTourForm(request.POST, request.FILES)
        if form.is_valid():
            tour = form.save(commit=False)
            tour.supplier = supplier
            tour.status = 'draft' # Default to draft
            tour.save()
            messages.success(request, 'Tour created successfully.')
            return redirect('supplier_tours')
        else:
            messages.error(request, 'Error creating tour. Please check the form.')
    else:
        form = SupplierTourForm()

    tours_list = Tour.objects.filter(supplier=supplier).order_by('-created_at')
    
    paginator = Paginator(tours_list, 10) # Show 10 tours per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/tour_supplier/pages/supplier_tours.html', {'supplier': supplier, 'tours': page_obj, 'form': form})

def supplier_tour_edit(request, tour_id):
    supplier_id = request.session.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Please login first.')
        return redirect('login_tour_supplier')
        
    supplier = TourSupplier.objects.get(id=supplier_id)
    tour = get_object_or_404(Tour, id=tour_id, supplier=supplier)
    
    # if request.method == 'POST':
    #     form = TourForm(request.POST, request.FILES, instance=tour)
    #     if form.is_valid():
    #         form.save()
    #         messages.success(request, 'Tour updated successfully.')
    #         return redirect('supplier_tours')
    # else:
    #     form = TourForm(instance=tour)
    
    return render(request, 'accounts/tour_supplier/pages/supplier_tour_edit.html', {'tour': tour})

def supplier_tour_delete(request, tour_id):
    supplier_id = request.session.get('supplier_id')
    if not supplier_id:
        messages.error(request, 'Please login first.')
        return redirect('login_tour_supplier')
        
    supplier = TourSupplier.objects.get(id=supplier_id)
    tour = get_object_or_404(Tour, id=tour_id, supplier=supplier)
    
    if request.method == 'POST':
        tour.delete()
        messages.success(request, 'Tour deleted successfully.')
        return redirect('supplier_tours')
        
    return render(request, 'accounts/tour_supplier/pages/supplier_tour_delete.html', {'tour': tour})

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
    
    total_tours = Tour.objects.filter(supplier=supplier).count()
    total_bookings = Booking.objects.filter(tour__supplier=supplier).count()
    
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