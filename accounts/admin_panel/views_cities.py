from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import City
from .decorators import permission_required_with_message
from .forms_additions import CityForm

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_city')
def city_list(request):
    search_query = request.GET.get('search', '')
    country = request.GET.get('country', '')
    region = request.GET.get('region', '')
    is_active = request.GET.get('is_active', '')
    
    cities = City.objects.select_related('country', 'region').all()
    
    if search_query:
        cities = cities.filter(
            Q(name__icontains=search_query) |
            Q(name_dk__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if country:
        cities = cities.filter(country_id=country)
    
    if region:
        cities = cities.filter(region_id=region)
    
    if is_active == 'true':
        cities = cities.filter(is_active=True)
    elif is_active == 'false':
        cities = cities.filter(is_active=False)
    
    cities = cities.order_by('name')
    paginator = Paginator(cities, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    from accounts.models import Country, DestinationRegion
    return render(request, 'accounts/admin/cities/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'country': country,
        'region': region,
        'is_active': is_active,
        'countries': Country.objects.all(),
        'regions': DestinationRegion.objects.all()
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_city')
def city_detail(request, pk):
    city = get_object_or_404(
        City.objects.select_related('country', 'region')
        .prefetch_related('tours', 'tours__supplier', 'tours__category'), 
        pk=pk
    )
    
    return render(request, 'accounts/admin/cities/detail.html', {
        'city': city
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_city')
def city_create(request):
    from accounts.models import Country, DestinationRegion
    if request.method == 'POST':
        form = CityForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'City created successfully!')
            return redirect('city_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CityForm()

    return render(request, 'accounts/admin/cities/form.html', {'form': form, 'title': 'Create City', 'countries': Country.objects.all(), 'regions': DestinationRegion.objects.all()})


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_city')
def city_edit(request, pk):
    from accounts.models import Country, DestinationRegion
    city = get_object_or_404(City, pk=pk)
    if request.method == 'POST':
        form = CityForm(request.POST, request.FILES, instance=city)
        if form.is_valid():
            form.save()
            messages.success(request, 'City updated successfully!')
            return redirect('city_detail', pk=city.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CityForm(instance=city)

    return render(request, 'accounts/admin/cities/form.html', {'form': form, 'city': city, 'title': 'Edit City', 'countries': Country.objects.all(), 'regions': DestinationRegion.objects.all()})


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_city')
def city_delete(request, pk):
    city = get_object_or_404(City, pk=pk)
    if request.method == 'POST':
        try:
            city.delete()
            messages.success(request, 'City deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting city: {str(e)}')
        return redirect('city_list')

    return render(request, 'accounts/admin/cities/delete_confirm.html', {'city': city})


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_city')
def city_toggle_active(request, pk):
    city = get_object_or_404(City, pk=pk)
    city.is_active = not city.is_active
    city.save()
    messages.success(request, f'City {"activated" if city.is_active else "deactivated"} successfully!')
    return redirect('city_detail', pk=city.pk)

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_city')
def city_toggle_popular(request, pk):
    city = get_object_or_404(City, pk=pk)
    city.is_popular = not city.is_popular
    city.save()
    messages.success(request, f'City marked as {"popular" if city.is_popular else "not popular"} successfully!')
    return redirect('city_detail', pk=city.pk)
