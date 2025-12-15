from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import ContactUs
from .forms import ContactUsForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_contactus')
def contactus_list(request):
    search_query = request.GET.get('search', '')
    contactus = ContactUs.objects.all()
    
    if search_query:
        contactus = contactus.filter(Q(email__icontains=search_query))
    
    paginator = Paginator(contactus, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/contactus/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_contactus')
def contactus_create(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact Us message added successfully!')
            return redirect('contactus_list')
    else:
        form = ContactUsForm()
    
    return render(request, 'accounts/admin/contactus/create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_contactus')
def contactus_edit(request, pk):
    contactus = get_object_or_404(ContactUs, pk=pk)
    
    if request.method == 'POST':
        form = ContactUsForm(request.POST, instance=contactus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact Us message updated successfully!')
            return redirect('contactus_list')
    else:
        form = ContactUsForm(instance=contactus)
    
    return render(request, 'accounts/admin/contactus/edit.html', {
        'form': form,
        'contactus': contactus
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_contactus')
def contactus_delete(request, pk):
    contactus = get_object_or_404(ContactUs, pk=pk)
    contactus.delete()
    messages.success(request, 'Contact Us message deleted successfully!')
    return redirect('contactus_list')
