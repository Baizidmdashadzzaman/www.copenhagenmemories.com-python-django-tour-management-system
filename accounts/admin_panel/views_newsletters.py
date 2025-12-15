from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Newsletter
from .forms import NewsletterForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_newsletter')
def newsletter_list(request):
    search_query = request.GET.get('search', '')
    newsletters = Newsletter.objects.all()
    
    if search_query:
        newsletters = newsletters.filter(Q(email__icontains=search_query))
    
    paginator = Paginator(newsletters, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/newsletters/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_newsletter')
def newsletter_create(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Newsletter subscriber added successfully!')
            return redirect('newsletter_list')
    else:
        form = NewsletterForm()
    
    return render(request, 'accounts/admin/newsletters/create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_newsletter')
def newsletter_edit(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    
    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Newsletter subscriber updated successfully!')
            return redirect('newsletter_list')
    else:
        form = NewsletterForm(instance=newsletter)
    
    return render(request, 'accounts/admin/newsletters/edit.html', {
        'form': form,
        'newsletter': newsletter
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_newsletter')
def newsletter_delete(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    newsletter.delete()
    messages.success(request, 'Newsletter subscriber deleted successfully!')
    return redirect('newsletter_list')
