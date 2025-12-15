from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Page
from .forms import PageForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_page')
def page_list(request):
    search_query = request.GET.get('search', '')
    pages = Page.objects.all()
    
    if search_query:
        pages = pages.filter(
            Q(title__icontains=search_query) | 
            Q(title_dk__icontains=search_query)
        )
    
    paginator = Paginator(pages, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/pages/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_page')
def page_create(request):
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Page created successfully!')
            return redirect('page_list')
    else:
        form = PageForm()
    
    return render(request, 'accounts/admin/pages/form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_page')
def page_edit(request, pk):
    page = get_object_or_404(Page, pk=pk)
    
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, 'Page updated successfully!')
            return redirect('page_list')
    else:
        form = PageForm(instance=page)
    
    return render(request, 'accounts/admin/pages/form.html', {
        'form': form,
        'page': page
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_page')
def page_delete(request, pk):
    page = get_object_or_404(Page, pk=pk)
    if request.method == 'POST':
        page.delete()
        messages.success(request, 'Page deleted successfully!')
        return redirect('page_list')
    return render(request, 'accounts/admin/pages/confirm_delete.html', {'page': page})
