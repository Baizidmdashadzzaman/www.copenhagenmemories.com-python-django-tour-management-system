from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import Slider
from .forms import SliderForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_slider')
def slider_list(request):
    search_query = request.GET.get('search', '')
    sliders = Slider.objects.all()
    
    if search_query:
        sliders = sliders.filter(
            Q(title__icontains=search_query) | 
            Q(title_dk__icontains=search_query) |
            Q(subtitle__icontains=search_query) |
            Q(subtitle_dk__icontains=search_query)
        )
    
    paginator = Paginator(sliders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/sliders/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_slider')
def slider_create(request):
    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slider created successfully!')
            return redirect('slider_list')
    else:
        form = SliderForm()
    
    return render(request, 'accounts/admin/sliders/create.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_slider')
def slider_edit(request, pk):
    slider = get_object_or_404(Slider, pk=pk)
    
    if request.method == 'POST':
        form = SliderForm(request.POST, request.FILES, instance=slider)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slider updated successfully!')
            return redirect('slider_list')
    else:
        form = SliderForm(instance=slider)
    
    return render(request, 'accounts/admin/sliders/edit.html', {
        'form': form,
        'slider': slider
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_slider')
def slider_delete(request, pk):
    slider = get_object_or_404(Slider, pk=pk)
    slider.delete()
    messages.success(request, 'Slider deleted successfully!')
    return redirect('slider_list')
