from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import BikeAddon
from .forms import BikeAddonForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_bikeaddon')
def bike_addon_list(request):
    search_query = request.GET.get('search', '')
    bike_addons = BikeAddon.objects.all()
    
    if search_query:
        bike_addons = bike_addons.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(bike_addons, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/bike_adons/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_bikeaddon')
def bike_addon_create(request):
    if request.method == 'POST':
        form = BikeAddonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bike Addon created successfully!')
            return redirect('bike_addon_list')
    else:
        form = BikeAddonForm()
    
    return render(request, 'accounts/admin/bike_adons/create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_bikeaddon')
def bike_addon_edit(request, pk):
    bike_addon = get_object_or_404(BikeAddon, pk=pk)
    
    if request.method == 'POST':
        form = BikeAddonForm(request.POST, request.FILES, instance=bike_addon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bike Addon updated successfully!')
            return redirect('bike_addon_list')
    else:
        form = BikeAddonForm(instance=bike_addon)
    
    return render(request, 'accounts/admin/bike_adons/edit.html', {
        'form': form,
        'bike_addon': bike_addon
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_bikeaddon')
def bike_addon_delete(request, pk):
    bike_addon = get_object_or_404(BikeAddon, pk=pk)
    bike_addon.delete()
    messages.success(request, 'Bike Addon deleted successfully!')
    return redirect('bike_addon_list')
