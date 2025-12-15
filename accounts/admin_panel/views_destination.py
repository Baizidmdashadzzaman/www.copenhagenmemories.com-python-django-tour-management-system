from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import DestinationRegion
from .forms import DestinationRegionForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_destinationregion')
def destination_region_list(request):
    search_query = request.GET.get('search', '')
    regions = DestinationRegion.objects.all()
    
    if search_query:
        regions = regions.filter(
            Q(name__icontains=search_query) | 
            Q(country__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(regions, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/destination_regions/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_destinationregion')
def destination_region_create(request):
    if request.method == 'POST':
        form = DestinationRegionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destination region created successfully!')
            return redirect('destination_region_list')
    else:
        form = DestinationRegionForm()
    
    return render(request, 'accounts/admin/destination_regions/create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_destinationregion')
def destination_region_edit(request, pk):
    region = get_object_or_404(DestinationRegion, pk=pk)
    
    if request.method == 'POST':
        form = DestinationRegionForm(request.POST, request.FILES, instance=region)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destination region updated successfully!')
            return redirect('destination_region_list')
    else:
        form = DestinationRegionForm(instance=region)
    
    return render(request, 'accounts/admin/destination_regions/edit.html', {
        'form': form,
        'region': region
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_destinationregion')
def destination_region_delete(request, pk):
    region = get_object_or_404(DestinationRegion, pk=pk)
    region.delete()
    messages.success(request, 'Destination region deleted successfully!')
    return redirect('destination_region_list')
