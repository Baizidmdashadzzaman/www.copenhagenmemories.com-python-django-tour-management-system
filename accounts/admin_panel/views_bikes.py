from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Bike
from .forms import BikeForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_bike')
def bike_list(request):
    search_query = request.GET.get('search', '')
    bikes = Bike.objects.all()
    
    if search_query:
        bikes = bikes.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(shortdescription__icontains=search_query)
        )
    
    paginator = Paginator(bikes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/bikes/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_bike')
def bike_create(request):
    if request.method == 'POST':
        form = BikeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bike created successfully!')
            return redirect('bike_list')
    else:
        form = BikeForm()
    
    return render(request, 'accounts/admin/bikes/create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_bike')
def bike_edit(request, pk):
    bike = get_object_or_404(Bike, pk=pk)
    
    if request.method == 'POST':
        form = BikeForm(request.POST, request.FILES, instance=bike)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bike updated successfully!')
            return redirect('bike_list')
    else:
        form = BikeForm(instance=bike)
    
    return render(request, 'accounts/admin/bikes/edit.html', {
        'form': form,
        'bike': bike
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_bike')
def bike_delete(request, pk):
    bike = get_object_or_404(Bike, pk=pk)
    bike.delete()
    messages.success(request, 'Bike deleted successfully!')
    return redirect('bike_list')
