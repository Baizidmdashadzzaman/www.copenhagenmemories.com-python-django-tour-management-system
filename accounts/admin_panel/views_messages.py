from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from accounts.models import CustomerMessage, Customer
from accounts.admin_panel.forms import CustomerMessageForm, MessageReplyForm
from accounts.admin_panel.decorators import admin_required

@login_required
@admin_required
def message_list(request):
    """Display all customer messages with filtering options"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Get latest message for each customer (conversation threads)
    conversations = CustomerMessage.objects.filter(
        parent_message__isnull=True
    ).select_related('customer__user', 'sender_admin')
    
    # Apply filters
    if search_query:
        conversations = conversations.filter(
            Q(customer__user__username__icontains=search_query) |
            Q(customer__user__first_name__icontains=search_query) |
            Q(customer__user__last_name__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    if status_filter == 'unread':
        conversations = conversations.filter(is_read=False)
    elif status_filter == 'read':
        conversations = conversations.filter(is_read=True)
    
    conversations = conversations.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(conversations, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Count unread messages
    unread_count = CustomerMessage.objects.filter(
        is_read=False, 
        sender_type='customer'
    ).count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/admin/messages/list.html', context)

@login_required
@admin_required
def message_thread(request, customer_id):
    """View message thread for a specific customer"""
    customer = get_object_or_404(Customer, pk=customer_id)
    
    # Get all messages for this customer
    thread_messages = CustomerMessage.objects.filter(
        customer=customer
    ).select_related('sender_admin').order_by('created_at')
    
    # Mark customer messages as read
    CustomerMessage.objects.filter(
        customer=customer, 
        sender_type='customer', 
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    # Handle reply form submission
    if request.method == 'POST':
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.customer = customer
            reply.sender_type = 'admin'
            reply.sender_admin = request.user
            reply.subject = f"Re: {thread_messages.first().subject if thread_messages.exists() else 'Message'}"
            
            # Link to parent message if exists
            if thread_messages.exists():
                reply.parent_message = thread_messages.first()
            
            reply.save()
            messages.success(request, 'Reply sent successfully!')
            return redirect('message_thread', customer_id=customer_id)
    else:
        form = MessageReplyForm()
    
    context = {
        'customer': customer,
        'thread_messages': thread_messages,
        'form': form,
    }
    return render(request, 'accounts/admin/messages/thread.html', context)

@login_required
@admin_required
def message_send(request, customer_id):
    """Send a new message to customer"""
    customer = get_object_or_404(Customer, pk=customer_id)
    
    if request.method == 'POST':
        form = CustomerMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.customer = customer
            message.sender_type = 'admin'
            message.sender_admin = request.user
            message.save()
            messages.success(request, f'Message sent to {customer.user.username} successfully!')
            return redirect('message_thread', customer_id=customer_id)
    else:
        form = CustomerMessageForm()
    
    context = {
        'customer': customer,
        'form': form,
    }
    return render(request, 'accounts/admin/messages/send.html', context)

@login_required
@admin_required
def message_mark_read(request, message_id):
    """Mark a message as read"""
    message = get_object_or_404(CustomerMessage, pk=message_id)
    message.is_read = True
    message.read_at = timezone.now()
    message.save()
    messages.success(request, 'Message marked as read!')
    return redirect('message_list')

@login_required
@admin_required
def message_delete(request, message_id):
    """Delete a message"""
    message = get_object_or_404(CustomerMessage, pk=message_id)
    customer_id = message.customer.id
    message.delete()
    messages.success(request, 'Message deleted successfully!')
    
    # Check if there are more messages for this customer
    if CustomerMessage.objects.filter(customer_id=customer_id).exists():
        return redirect('message_thread', customer_id=customer_id)
    else:
        return redirect('message_list')
