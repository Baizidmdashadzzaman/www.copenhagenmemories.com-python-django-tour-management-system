from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Customer
from .forms import CustomerForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_customer')
def customer_list(request):
    search_query = request.GET.get('search', '')
    customers = Customer.objects.select_related('user').all()
    
    if search_query:
        customers = customers.filter(
            Q(user__username__icontains=search_query) | 
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    paginator = Paginator(customers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/customers/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_customer')
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Customer created successfully!')
                return redirect('customer_list')
            except Exception as e:
                messages.error(request, f'Error creating customer: {str(e)}')
    else:
        form = CustomerForm()
    
    return render(request, 'accounts/admin/customers/create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_customer')
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Customer updated successfully!')
                return redirect('customer_list')
            except Exception as e:
                messages.error(request, f'Error updating customer: {str(e)}')
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'accounts/admin/customers/edit.html', {
        'form': form,
        'customer': customer
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_customer')
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    user = customer.user
    customer.delete()
    user.delete()  # Also delete the associated user
    messages.success(request, 'Customer deleted successfully!')
    return redirect('customer_list')

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_booking')
def customer_booking_list(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    bookings = customer.bookings.select_related('tour', 'schedule').all().order_by('-created_at')
    
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/customers/booking_list.html', {
        'customer': customer,
        'page_obj': page_obj
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_customer')
def customer_wishlist(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    wishlist_items = customer.wishlist.select_related('tour').all().order_by('-created_at')
    
    paginator = Paginator(wishlist_items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/customers/wishlist.html', {
        'customer': customer,
        'page_obj': page_obj
    })
