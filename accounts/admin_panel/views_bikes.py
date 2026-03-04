from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Bike, BikeAddon, BikeAddonPrice
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
            bike = form.save()
            
            # Handle addons from jquery-repeater
            # jquery-repeater sends data like: addons-group[0][addon_id], addons-group[0][addon_price], etc.
            # But we can also try to get them by looking for keys containing 'addon_id' and 'addon_price'
            # or by iterating through the expected index patterns.
            
            print(f"DEBUG: Processing addons for new bike ID: {bike.id}")
            i = 0
            while True:
                # Common pattern for jquery-repeater: group-name[index][field-name]
                addon_id_key = f'addons-group[{i}][addon_id]'
                addon_price_key = f'addons-group[{i}][addon_price]'
                
                if addon_id_key in request.POST:
                    addon_id = request.POST.get(addon_id_key)
                    price = request.POST.get(addon_price_key)
                    
                    if addon_id and price:
                        try:
                            addon = BikeAddon.objects.get(id=addon_id)
                            BikeAddonPrice.objects.create(
                                bike=bike,
                                addon=addon,
                                price=price
                            )
                            print(f"DEBUG: Created addon {i}: ID={addon_id}, Price={price}")
                        except Exception as e:
                            print(f"DEBUG: Error saving addon {i}: {e}")
                    i += 1
                else:
                    # Also check for non-grouped names if repeater fails to group
                    if i == 0:
                        addon_ids = request.POST.getlist('addon_id')
                        addon_prices = request.POST.getlist('addon_price')
                        if addon_ids and addon_prices:
                            for aid, apr in zip(addon_ids, addon_prices):
                                if aid and apr:
                                    try:
                                        addon = BikeAddon.objects.get(id=aid)
                                        BikeAddonPrice.objects.create(bike=bike, addon=addon, price=apr)
                                        print(f"DEBUG: Created addon from list: ID={aid}, Price={apr}")
                                    except Exception as e:
                                        print(f"DEBUG: Error saving addon from list: {e}")
                    break

            messages.success(request, 'Bike created successfully!')
            return redirect('bike_list')
        else:
            print(f"DEBUG: BikeForm Errors (Create): {form.errors}")
    else:
        form = BikeForm()
    
    addons_list = BikeAddon.objects.filter(status='active').order_by('title')
    return render(request, 'accounts/admin/bikes/create.html', {
        'form': form,
        'addons_list': addons_list
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_bike')
def bike_edit(request, pk):
    bike = get_object_or_404(Bike, pk=pk)
    
    if request.method == 'POST':
        form = BikeForm(request.POST, request.FILES, instance=bike)
        if form.is_valid():
            bike = form.save()
            print(f"DEBUG: bike_edit - Main form saved for bike ID: {bike.id}")
            
            # Update addons - Always refresh if it's a POST
            has_repeater_data = any('addons-group' in key for key in request.POST.keys())
            
            if has_repeater_data or 'addon_id' in request.POST:
                print(f"DEBUG: Refreshing addons for bike ID: {bike.id}")
                bike.bike_addons.all().delete()
                
                i = 0
                while True:
                    addon_id_key = f'addons-group[{i}][addon_id]'
                    addon_price_key = f'addons-group[{i}][addon_price]'
                    
                    if addon_id_key in request.POST:
                        addon_id = request.POST.get(addon_id_key)
                        price = request.POST.get(addon_price_key)
                        
                        if addon_id and price:
                            try:
                                addon = BikeAddon.objects.get(id=addon_id)
                                BikeAddonPrice.objects.create(
                                    bike=bike,
                                    addon=addon,
                                    price=price
                                )
                                print(f"DEBUG: Re-created addon {i}: ID={addon_id}, Price={price}")
                            except Exception as e:
                                print(f"DEBUG: Error saving addon {i}: {e}")
                        i += 1
                    else:
                        # Fallback for non-grouped names
                        if i == 0:
                            addon_ids = request.POST.getlist('addon_id')
                            addon_prices = request.POST.getlist('addon_price')
                            if addon_ids and addon_prices:
                                for aid, apr in zip(addon_ids, addon_prices):
                                    if aid and apr:
                                        try:
                                            addon = BikeAddon.objects.get(id=aid)
                                            BikeAddonPrice.objects.create(bike=bike, addon=addon, price=apr)
                                            print(f"DEBUG: Created addon from list: ID={aid}, Price={apr}")
                                        except Exception as e:
                                            print(f"DEBUG: Error saving addon from list: {e}")
                        break
            else:
                print("DEBUG: No addon data found in POST, skipping addon refresh")

            messages.success(request, 'Bike updated successfully!')
            return redirect('bike_list')
        else:
            print(f"DEBUG: BikeForm Errors (Edit): {form.errors}")
    else:
        form = BikeForm(instance=bike)
    
    addons_list = BikeAddon.objects.filter(status='active').order_by('title')
    current_addons = bike.bike_addons.all()
    print(f"DEBUG: bike_edit view - Bike: {bike.title}, ID: {bike.id}, Count of current_addons: {current_addons.count()}")
    for ca in current_addons:
        print(f"DEBUG: Found addon {ca.addon.title} with price {ca.price}")
    
    return render(request, 'accounts/admin/bikes/edit.html', {
        'form': form,
        'bike': bike,
        'addons_list': addons_list,
        'current_addons': current_addons
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_bike')
def bike_delete(request, pk):
    bike = get_object_or_404(Bike, pk=pk)
    bike.delete()
    messages.success(request, 'Bike deleted successfully!')
    return redirect('bike_list')
