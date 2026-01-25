from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Souvenir, SouvenirOrder, SouvenirOrderItem
from .decorators import permission_required_with_message
from .forms_additions import SouvenirForm, SouvenirOrderAdminForm, SouvenirOrderItemFormSet

# ... (existing souvenir views)

@login_required
@user_passes_test(lambda u: u.is_staff)
def souvenir_order_edit(request, pk):
    order = get_object_or_404(SouvenirOrder, pk=pk)
    if request.method == 'POST':
        form = SouvenirOrderAdminForm(request.POST, instance=order)
        formset = SouvenirOrderItemFormSet(request.POST, instance=order, prefix='items')
        if form.is_valid() and formset.is_valid():
            # Calculate total amount automatically
            total = 0
            # Save formset with commit=False to get access to instances if needed, 
            # though here we mainly care about cleaned_data for calculation
            for item_form in formset:
                if not item_form.cleaned_data.get('DELETE', False):
                    price = item_form.cleaned_data.get('price', 0)
                    qty = item_form.cleaned_data.get('quantity', 0)
                    total += price * qty
            
            order = form.save(commit=False)
            order.total_amount = total
            order.save()
            
            formset.save()
            messages.success(request, 'Order updated successfully!')
            return redirect('souvenir_order_detail', pk=pk)
    else:
        form = SouvenirOrderAdminForm(instance=order)
        formset = SouvenirOrderItemFormSet(instance=order, prefix='items')
    
    return render(request, 'accounts/admin/souvenir_orders/form.html', {
        'form': form,
        'formset': formset,
        'order': order,
        'title': f'Edit Order #{order.order_number}'
    })

# ... (existing souvenir views)

@login_required
@user_passes_test(lambda u: u.is_staff)
def souvenir_order_list(request):
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    orders = SouvenirOrder.objects.all()
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    if status:
        orders = orders.filter(status=status)
    
    orders = orders.order_by('-created_at')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/souvenir_orders/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status': status,
        'status_choices': SouvenirOrder._meta.get_field('status').choices
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def souvenir_order_detail(request, pk):
    order = get_object_or_404(SouvenirOrder, pk=pk)
    return render(request, 'accounts/admin/souvenir_orders/detail.html', {
        'order': order,
        'title': f'Order {order.order_number}'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def souvenir_order_invoice(request, pk):
    order = get_object_or_404(SouvenirOrder, pk=pk)
    return render(request, 'accounts/admin/souvenir_orders/invoice.html', {
        'order': order,
        'title': f'Invoice #{order.order_number}'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def souvenir_order_status_update(request, pk):
    order = get_object_or_404(SouvenirOrder, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(SouvenirOrder.ORDER_STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status.')
    return redirect('souvenir_order_detail', pk=pk)

@login_required
@user_passes_test(lambda u: u.is_staff)
def souvenir_order_delete(request, pk):
    order = get_object_or_404(SouvenirOrder, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully!')
        return redirect('souvenir_order_list')
    return render(request, 'accounts/admin/souvenir_orders/delete_confirm.html', {'order': order})

@login_required
@user_passes_test(lambda u: u.is_staff)
# @permission_required_with_message('accounts.view_souvenir')
def souvenir_list(request):
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    souvenirs = Souvenir.objects.all()
    
    if search_query:
        souvenirs = souvenirs.filter(
            Q(title__icontains=search_query) |
            Q(title_dk__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if status:
        souvenirs = souvenirs.filter(status=status)
    
    souvenirs = souvenirs.order_by('-created_at')
    paginator = Paginator(souvenirs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/souvenirs/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status': status,
        'status_choices': Souvenir._meta.get_field('status').choices
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
# @permission_required_with_message('accounts.add_souvenir')
def souvenir_create(request):
    if request.method == 'POST':
        form = SouvenirForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Souvenir created successfully!')
            return redirect('souvenir_list')
    else:
        form = SouvenirForm()
    
    return render(request, 'accounts/admin/souvenirs/form.html', {
        'form': form,
        'title': 'Create Souvenir'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
# @permission_required_with_message('accounts.change_souvenir')
def souvenir_edit(request, pk):
    souvenir = get_object_or_404(Souvenir, pk=pk)
    if request.method == 'POST':
        form = SouvenirForm(request.POST, request.FILES, instance=souvenir)
        if form.is_valid():
            form.save()
            messages.success(request, 'Souvenir updated successfully!')
            return redirect('souvenir_list')
    else:
        form = SouvenirForm(instance=souvenir)
    
    return render(request, 'accounts/admin/souvenirs/form.html', {
        'form': form,
        'souvenir': souvenir,
        'title': 'Edit Souvenir'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
# @permission_required_with_message('accounts.delete_souvenir')
def souvenir_delete(request, pk):
    souvenir = get_object_or_404(Souvenir, pk=pk)
    if request.method == 'POST':
        souvenir.delete()
        messages.success(request, 'Souvenir deleted successfully!')
        return redirect('souvenir_list')
    
    return render(request, 'accounts/admin/souvenirs/delete_confirm.html', {'souvenir': souvenir})
