from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Country
from .forms import CountryForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_country')
def country_list(request):
    search_query = request.GET.get('search', '')
    countries = Country.objects.all()
    
    if search_query:
        countries = countries.filter(
            Q(name__icontains=search_query) | 
            Q(code__icontains=search_query)
        )
    
    paginator = Paginator(countries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/countries/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_country')
def country_create(request):
    if request.method == 'POST':
        form = CountryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Country created successfully!')
            return redirect('country_list')
    else:
        form = CountryForm()
    
    return render(request, 'accounts/admin/countries/create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_country')
def country_edit(request, pk):
    country = get_object_or_404(Country, pk=pk)
    
    if request.method == 'POST':
        form = CountryForm(request.POST, request.FILES, instance=country)
        if form.is_valid():
            form.save()
            messages.success(request, 'Country updated successfully!')
            return redirect('country_list')
    else:
        form = CountryForm(instance=country)
    
    return render(request, 'accounts/admin/countries/edit.html', {
        'form': form,
        'country': country
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_country')
def country_delete(request, pk):
    country = get_object_or_404(Country, pk=pk)
    country.delete()
    messages.success(request, 'Country deleted successfully!')
    return redirect('country_list')
