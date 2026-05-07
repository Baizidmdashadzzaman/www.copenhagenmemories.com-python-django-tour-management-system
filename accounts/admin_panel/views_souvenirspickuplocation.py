from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import SouvenirPickuplocation
from .forms import SouvenirPickuplocationForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_souvenirpickuplocation')
def souvenirpickuplocation_list(request):
    search_query = request.GET.get('search', '')
    souvenirpickuplocations = SouvenirPickuplocation.objects.all()
    
    if search_query:
        souvenirpickuplocations = souvenirpickuplocations.filter(
            Q(name__icontains=search_query) | 
            Q(contact_person_name__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    paginator = Paginator(souvenirpickuplocations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/souvenirpickuplocation/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_souvenirpickuplocation')
def souvenirpickuplocation_create(request):
    if request.method == 'POST':
        form = SouvenirPickuplocationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Souvenir Pickup Location added successfully!')
                return redirect('souvenirpickuplocation_list')
            except Exception as e:
                messages.error(request, f'Error adding Souvenir Pickup Location: {str(e)}')
    else:
        form = SouvenirPickuplocationForm()
    
    return render(request, 'accounts/admin/souvenirpickuplocation/form.html', {
        'form': form,
        'title': 'Add Souvenir Pickup Location'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_souvenirpickuplocation')
def souvenirpickuplocation_edit(request, pk):
    souvenirpickuplocation = get_object_or_404(SouvenirPickuplocation, pk=pk)
    
    if request.method == 'POST':
        form = SouvenirPickuplocationForm(request.POST, request.FILES, instance=souvenirpickuplocation)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Souvenir Pickup Location updated successfully!')
                return redirect('souvenirpickuplocation_list')
            except Exception as e:
                messages.error(request, f'Error updating Souvenir Pickup Location: {str(e)}')
    else:
        form = SouvenirPickuplocationForm(instance=souvenirpickuplocation)
    
    return render(request, 'accounts/admin/souvenirpickuplocation/form.html', {
        'form': form,
        'souvenirpickuplocation': souvenirpickuplocation,
        'title': 'Edit Souvenir Pickup Location'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_souvenirpickuplocation')
def souvenirpickuplocation_delete(request, pk):
    souvenirpickuplocation = get_object_or_404(SouvenirPickuplocation, pk=pk)
    souvenirpickuplocation.delete()
    messages.success(request, 'Souvenir Pickup Location deleted successfully!')
    return redirect('souvenirpickuplocation_list')
