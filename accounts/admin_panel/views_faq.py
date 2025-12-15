from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import FAQ
from .forms import FAQForm

@login_required
@user_passes_test(lambda u: u.is_staff)
def faq_list(request):
    search_query = request.GET.get('search', '')
    faqs = FAQ.objects.all()
    
    if search_query:
        faqs = faqs.filter(
            Q(qus_en__icontains=search_query) | 
            Q(qus_dk__icontains=search_query) |
            Q(ans_en__icontains=search_query) |
            Q(ans_dk__icontains=search_query)
        )
    
    paginator = Paginator(faqs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/faq/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def faq_create(request):
    if request.method == 'POST':
        form = FAQForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'FAQ created successfully!')
            return redirect('faq_list')
    else:
        form = FAQForm()
    
    return render(request, 'accounts/admin/faq/form.html', {
        'form': form,
        'action': 'Create'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def faq_edit(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    
    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, 'FAQ updated successfully!')
            return redirect('faq_list')
    else:
        form = FAQForm(instance=faq)
    
    return render(request, 'accounts/admin/faq/form.html', {
        'form': form,
        'faq': faq,
        'action': 'Edit'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def faq_delete(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    
    if request.method == 'POST':
        faq.delete()
        messages.success(request, 'FAQ deleted successfully!')
        return redirect('faq_list')
    
    return render(request, 'accounts/admin/faq/delete.html', {'faq': faq})
