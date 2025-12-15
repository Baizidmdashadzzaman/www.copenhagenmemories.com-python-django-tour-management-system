from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.models import TourSupplier
from accounts.admin_panel.forms import TourSupplierForm
from django.db.models import Q
from django.core.paginator import Paginator
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_toursupplier')
def tour_supplier_list(request):
    query = request.GET.get('q')
    suppliers_list = TourSupplier.objects.all().order_by('-created_at')
    
    if query:
        suppliers_list = suppliers_list.filter(
            Q(company_name__icontains=query) | 
            Q(contact_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )
    
    paginator = Paginator(suppliers_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/tour_suppliers/list.html', {
        'page_obj': page_obj,
        'search_query': query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_toursupplier')
def tour_supplier_create(request):
    if request.method == 'POST':
        form = TourSupplierForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tour Supplier created successfully!')
            return redirect('tour_supplier_list')
    else:
        form = TourSupplierForm()
    
    return render(request, 'accounts/admin/tour_suppliers/create.html', {
        'form': form,
        'title': 'Create Tour Supplier'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_toursupplier')
def tour_supplier_edit(request, pk):
    supplier = get_object_or_404(TourSupplier, pk=pk)
    if request.method == 'POST':
        form = TourSupplierForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tour Supplier updated successfully!')
            return redirect('tour_supplier_list')
    else:
        form = TourSupplierForm(instance=supplier)
    
    return render(request, 'accounts/admin/tour_suppliers/edit.html', {
        'form': form,
        'title': 'Edit Tour Supplier',
        'supplier': supplier
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_toursupplier')
def tour_supplier_delete(request, pk):
    supplier = get_object_or_404(TourSupplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Tour Supplier deleted successfully!')
        return redirect('tour_supplier_list')
    return redirect('tour_supplier_list')
