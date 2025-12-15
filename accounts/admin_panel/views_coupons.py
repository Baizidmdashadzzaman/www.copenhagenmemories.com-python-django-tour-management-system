from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Coupon, CouponUsage
from .decorators import permission_required_with_message
from .forms_additions import CouponForm

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_coupon')
def coupon_list(request):
    search_query = request.GET.get('search', '')
    is_active = request.GET.get('is_active', '')
    
    coupons = Coupon.objects.all()
    
    if search_query:
        coupons = coupons.filter(
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(description_dk__icontains=search_query)
        )
    
    if is_active == 'true':
        coupons = coupons.filter(is_active=True)
    elif is_active == 'false':
        coupons = coupons.filter(is_active=False)
    
    coupons = coupons.order_by('-created_at')
    paginator = Paginator(coupons, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/coupons/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'is_active': is_active
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_coupon')
def coupon_detail(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    usages = coupon.usages.select_related('customer__user', 'booking').all()
    
    return render(request, 'accounts/admin/coupons/detail.html', {
        'coupon': coupon,
        'usages': usages
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_coupon')
def coupon_create(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created successfully!')
            return redirect('coupon_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CouponForm()

    return render(request, 'accounts/admin/coupons/form.html', {'form': form, 'title': 'Create Coupon'})


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_coupon')
def coupon_edit(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon updated successfully!')
            return redirect('coupon_detail', pk=coupon.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CouponForm(instance=coupon)

    return render(request, 'accounts/admin/coupons/form.html', {'form': form, 'coupon': coupon, 'title': 'Edit Coupon'})


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_coupon')
def coupon_delete(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        try:
            coupon.delete()
            messages.success(request, 'Coupon deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting coupon: {str(e)}')
        return redirect('coupon_list')

    return render(request, 'accounts/admin/coupons/delete_confirm.html', {'coupon': coupon})


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_coupon')
def coupon_toggle_active(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    coupon.is_active = not coupon.is_active
    coupon.save()
    messages.success(request, f'Coupon {"activated" if coupon.is_active else "deactivated"} successfully!')
    return redirect('coupon_detail', pk=coupon.pk)
