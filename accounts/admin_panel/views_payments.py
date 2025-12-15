from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Payment
from .decorators import permission_required_with_message
from .forms_additions import PaymentForm

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_payment')
def payment_list(request):
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    payment_method = request.GET.get('payment_method', '')
    
    payments = Payment.objects.select_related('booking', 'booking__customer', 'booking__tour').all()
    
    if search_query:
        payments = payments.filter(
            Q(transaction_id__icontains=search_query) |
            Q(booking__booking_number__icontains=search_query) |
            Q(booking__customer__user__username__icontains=search_query)
        )
    
    if status:
        payments = payments.filter(status=status)
    
    if payment_method:
        payments = payments.filter(payment_method=payment_method)
    
    payments = payments.order_by('-created_at')
    paginator = Paginator(payments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/payments/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status': status,
        'payment_method': payment_method,
        'status_choices': Payment._meta.get_field('status').choices,
        'payment_method_choices': Payment._meta.get_field('payment_method').choices
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_payment')
def payment_detail(request, pk):
    payment = get_object_or_404(Payment.objects.select_related('booking', 'booking__customer__user', 'booking__tour'), pk=pk)
    
    return render(request, 'accounts/admin/payments/detail.html', {
        'payment': payment
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_payment')
def payment_status_update(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Payment._meta.get_field('status').choices):
            payment.status = new_status
            payment.save()
            messages.success(request, f'Payment status updated to {new_status}!')
            return redirect('payment_detail', pk=payment.pk)
        else:
            messages.error(request, 'Invalid status!')
    
    return render(request, 'accounts/admin/payments/status_update.html', {
        'payment': payment,
        'status_choices': Payment._meta.get_field('status').choices
    })
