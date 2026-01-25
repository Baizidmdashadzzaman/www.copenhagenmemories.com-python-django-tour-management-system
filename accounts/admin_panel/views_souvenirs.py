from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Souvenir
from .decorators import permission_required_with_message
from .forms_additions import SouvenirForm

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
