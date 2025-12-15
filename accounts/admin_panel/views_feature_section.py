from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import FeatureSection
from .forms import FeatureSectionForm
from .decorators import permission_required_with_message

@login_required # turbo
@user_passes_test(lambda u: u.is_staff)
#@permission_required_with_message('accounts.view_featuresection')
def feature_section_list(request):
    search_query = request.GET.get('search', '')
    feature_sections = FeatureSection.objects.all()
    
    if search_query:
        feature_sections = feature_sections.filter(
            Q(title__icontains=search_query) | 
            Q(title_dk__icontains=search_query)
        )
    
    paginator = Paginator(feature_sections, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/feature_section/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required # turbo
@user_passes_test(lambda u: u.is_staff)
#@permission_required_with_message('accounts.add_featuresection')
def feature_section_create(request):
    if request.method == 'POST':
        form = FeatureSectionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feature Section created successfully!')
            return redirect('feature_section_list')
    else:
        form = FeatureSectionForm()
    
    return render(request, 'accounts/admin/feature_section/form.html', {'form': form, 'title': 'Add Feature Section'})

@login_required # turbo
@user_passes_test(lambda u: u.is_staff)
#@permission_required_with_message('accounts.change_featuresection')
def feature_section_edit(request, pk):
    feature_section = get_object_or_404(FeatureSection, pk=pk)
    
    if request.method == 'POST':
        form = FeatureSectionForm(request.POST, request.FILES, instance=feature_section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feature Section updated successfully!')
            return redirect('feature_section_list')
    else:
        form = FeatureSectionForm(instance=feature_section)
    
    return render(request, 'accounts/admin/feature_section/form.html', {
        'form': form,
        'feature_section': feature_section,
        'title': 'Edit Feature Section'
    })

@login_required # turbo
@user_passes_test(lambda u: u.is_staff)
#@permission_required_with_message('accounts.delete_featuresection')
def feature_section_delete(request, pk):
    feature_section = get_object_or_404(FeatureSection, pk=pk)
    if request.method == 'POST':
        feature_section.delete()
        messages.success(request, 'Feature Section deleted successfully!')
        return redirect('feature_section_list')
    return render(request, 'accounts/admin/feature_section/confirm_delete.html', {'feature_section': feature_section})

from django.http import JsonResponse
from accounts.models import Tour, FeatureSectionTour

@login_required 
@user_passes_test(lambda u: u.is_staff)
def feature_section_tours(request, pk):
    feature_section = get_object_or_404(FeatureSection, pk=pk)
    tours = FeatureSectionTour.objects.filter(feature_section=feature_section).select_related('tour')
    
    return render(request, 'accounts/admin/feature_section/tours.html', {
        'feature_section': feature_section,
        'tours': tours
    })

@login_required 
@user_passes_test(lambda u: u.is_staff)
def feature_section_add_tour(request, pk):
    feature_section = get_object_or_404(FeatureSection, pk=pk)
    if request.method == 'POST':
        tour_id = request.POST.get('tour_id')
        if tour_id:
            tour = get_object_or_404(Tour, pk=tour_id)
            # Check if already exists
            if not FeatureSectionTour.objects.filter(feature_section=feature_section, tour=tour).exists():
                FeatureSectionTour.objects.create(feature_section=feature_section, tour=tour)
                messages.success(request, 'Tour added to section successfully!')
            else:
                messages.warning(request, 'Tour is already in this section.')
        else:
            messages.error(request, 'No tour selected.')
    
    return redirect('feature_section_tours', pk=pk)

@login_required 
@user_passes_test(lambda u: u.is_staff)
def feature_section_remove_tour(request, pk, tour_id):
    feature_section = get_object_or_404(FeatureSection, pk=pk)
    if request.method == 'POST':
        FeatureSectionTour.objects.filter(feature_section=feature_section, tour_id=tour_id).delete()
        messages.success(request, 'Tour removed from section successfully!')
    
    return redirect('feature_section_tours', pk=pk)

@login_required 
@user_passes_test(lambda u: u.is_staff)
def search_tours_ajax(request):
    query = request.GET.get('q', '')
    if query:
        tours = Tour.objects.filter(
            Q(title__icontains=query) | 
            Q(title_dk__icontains=query)
        ).values('id', 'title', 'main_image')[:10]
    else:
        # Return recent 10 tours if no query
        tours = Tour.objects.all().order_by('-created_at').values('id', 'title', 'main_image')[:10]
        
    results = []
    for tour in tours:
        results.append({
            'id': tour['id'],
            'text': tour['title'],
            'image': tour['main_image'] if tour['main_image'] else None
        })
    return JsonResponse({'results': results})
