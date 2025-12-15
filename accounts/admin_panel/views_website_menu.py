from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import WebsiteMenu
from .forms import WebsiteMenuForm

@login_required # turbo
@user_passes_test(lambda u: u.is_staff)
def website_menu_list(request):
    search_query = request.GET.get('search', '')
    menus = WebsiteMenu.objects.all()
    
    if search_query:
        menus = menus.filter(
            Q(title__icontains=search_query) | 
            Q(title_dk__icontains=search_query)
        )
    
    paginator = Paginator(menus, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/website_menu/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required # turbo
@user_passes_test(lambda u: u.is_staff)
def website_menu_create(request):
    if request.method == 'POST':
        form = WebsiteMenuForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Website Menu created successfully!')
            return redirect('website_menu_list')
    else:
        form = WebsiteMenuForm()
    
    return render(request, 'accounts/admin/website_menu/form.html', {'form': form, 'title': 'Add Website Menu'})

@login_required # turbo
@user_passes_test(lambda u: u.is_staff)
def website_menu_edit(request, pk):
    menu = get_object_or_404(WebsiteMenu, pk=pk)
    
    if request.method == 'POST':
        form = WebsiteMenuForm(request.POST, request.FILES, instance=menu)
        if form.is_valid():
            form.save()
            messages.success(request, 'Website Menu updated successfully!')
            return redirect('website_menu_list')
    else:
        form = WebsiteMenuForm(instance=menu)
    
    return render(request, 'accounts/admin/website_menu/form.html', {
        'form': form,
        'menu': menu,
        'title': 'Edit Website Menu'
    })

@login_required # turbo
@user_passes_test(lambda u: u.is_staff)
def website_menu_delete(request, pk):
    menu = get_object_or_404(WebsiteMenu, pk=pk)
    if request.method == 'POST':
        menu.delete()
        messages.success(request, 'Website Menu deleted successfully!')
        return redirect('website_menu_list')
    return render(request, 'accounts/admin/website_menu/confirm_delete.html', {'menu': menu})

from accounts.models import WebsiteSubMenu
from .forms import WebsiteSubMenuForm

@login_required # turbo
@user_passes_test(lambda u: u.is_staff)
def website_submenu_list(request, menu_id):
    menu = get_object_or_404(WebsiteMenu, pk=menu_id)
    submenus = WebsiteSubMenu.objects.filter(menu=menu)
    
    return render(request, 'accounts/admin/website_menu/submenu/list.html', {
        'menu': menu,
        'submenus': submenus
    })

@login_required # turbo
@user_passes_test(lambda u: u.is_staff)
def website_submenu_create(request, menu_id):
    menu = get_object_or_404(WebsiteMenu, pk=menu_id)
    
    if request.method == 'POST':
        form = WebsiteSubMenuForm(request.POST)
        if form.is_valid():
            submenu = form.save(commit=False)
            submenu.menu = menu
            submenu.save()
            messages.success(request, 'Submenu created successfully!')
            return redirect('website_submenu_list', menu_id=menu.pk)
    else:
        form = WebsiteSubMenuForm()
    
    return render(request, 'accounts/admin/website_menu/submenu/form.html', {
        'form': form, 
        'menu': menu,
        'title': 'Add Submenu'
    })

@login_required # turbo
@user_passes_test(lambda u: u.is_staff)
def website_submenu_edit(request, pk):
    submenu = get_object_or_404(WebsiteSubMenu, pk=pk)
    
    if request.method == 'POST':
        form = WebsiteSubMenuForm(request.POST, instance=submenu)
        if form.is_valid():
            form.save()
            messages.success(request, 'Submenu updated successfully!')
            return redirect('website_submenu_list', menu_id=submenu.menu.pk)
    else:
        form = WebsiteSubMenuForm(instance=submenu)
    
    return render(request, 'accounts/admin/website_menu/submenu/form.html', {
        'form': form,
        'menu': submenu.menu,
        'submenu': submenu,
        'title': 'Edit Submenu'
    })

@login_required # turbo
@user_passes_test(lambda u: u.is_staff)
def website_submenu_delete(request, pk):
    submenu = get_object_or_404(WebsiteSubMenu, pk=pk)
    menu_id = submenu.menu.pk
    if request.method == 'POST':
        submenu.delete()
        messages.success(request, 'Submenu deleted successfully!')
        return redirect('website_submenu_list', menu_id=menu_id)
    return render(request, 'accounts/admin/website_menu/submenu/confirm_delete.html', {'submenu': submenu})
