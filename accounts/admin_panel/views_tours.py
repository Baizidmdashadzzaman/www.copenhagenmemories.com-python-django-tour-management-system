from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Value
from django.db.models.functions import Coalesce
from accounts.models import Tour, TourImage, TourHighlight, TourIncluded, TourExcluded, TourItinerary, TourRequirement, TourFAQ, TourPricing, TourSchedule, TourBlackoutDate
from .decorators import permission_required_with_message
from .forms_additions import TourForm, TourImageForm, TourHighlightForm, TourIncludedForm, TourExcludedForm, TourItineraryForm, TourRequirementForm, TourFAQForm, TourPricingForm, TourScheduleForm, TourBlackoutDateForm

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tour')
def tour_list(request):
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    tours = Tour.objects.select_related('supplier', 'category', 'destination_region', 'city').annotate(
        calculated_average_rating=Coalesce(Avg('reviews__overall_rating'), Value(0.0)),
        calculated_total_reviews=Count('reviews')
    ).order_by('-id')
    
    if search_query:
        tours = tours.filter(
            Q(title__icontains=search_query) |
            Q(title_dk__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if status:
        tours = tours.filter(status=status)
    
    paginator = Paginator(tours, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/tours/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status': status,
        'status_choices': Tour._meta.get_field('status').choices
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_tour')
def tour_create(request):
    # Use TourForm with proper Bootstrap widget classes
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tour created successfully!')
            return redirect('tour_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TourForm()

    return render(request, 'accounts/admin/tours/form.html', {'form': form, 'title': 'Create Tour'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tour')
def tour_edit(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES, instance=tour)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tour updated successfully!')
            return redirect('tour_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TourForm(instance=tour)

    return render(request, 'accounts/admin/tours/form.html', {'form': form, 'tour': tour, 'title': 'Edit Tour'})


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_tour')
def tour_delete(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    if request.method == 'POST':
        try:
            tour.delete()
            messages.success(request, 'Tour deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting tour: {str(e)}')
        return redirect('tour_list')
    
    return render(request, 'accounts/admin/tours/delete_confirm.html', {'tour': tour})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tour')
def tour_view(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    context = {
        'tour': tour,
        'images': tour.images.all().order_by('display_order'),
        'highlights': tour.highlights.all().order_by('display_order'),
        'included_items': tour.included_items.all().order_by('display_order'),
        'excluded_items': tour.excluded_items.all().order_by('display_order'),
        'itinerary_steps': tour.itinerary_steps.all().order_by('step_number'),
        'requirements': tour.requirements.all().order_by('display_order'),
        'faqs': tour.faqs.all().order_by('display_order'),
        'pricing_options': tour.pricing_options.all(),
        'schedules': tour.schedules.all().order_by('date', 'start_time'),
        'blackout_dates': tour.blackout_dates.all().order_by('start_date'),
    }
    return render(request, 'accounts/admin/tours/view.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tourimage')
def tour_image_list(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    images = tour.images.all().order_by('display_order')
    
    return render(request, 'accounts/admin/tours/images_list.html', {
        'tour': tour,
        'images': images
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tourhighlight')
def tour_highlights_list(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    highlights = tour.highlights.all().order_by('display_order')
    
    return render(request, 'accounts/admin/tours/highlights_list.html', {
        'tour': tour,
        'highlights': highlights
    })


# Tour Image CRUD
@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_tourimage')
def tour_image_create(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    
    if request.method == 'POST':
        form = TourImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.tour = tour
            image.save()
            messages.success(request, 'Image uploaded successfully!')
            return redirect('tour_image_list', tour_id=tour_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TourImageForm()
    
    return render(request, 'accounts/admin/tours/image_form.html', {
        'form': form,
        'tour': tour,
        'title': 'Upload Image'
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tourimage')
def tour_image_edit(request, tour_id, image_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    image = get_object_or_404(TourImage, pk=image_id, tour=tour)
    
    if request.method == 'POST':
        form = TourImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            messages.success(request, 'Image updated successfully!')
            return redirect('tour_image_list', tour_id=tour_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TourImageForm(instance=image)
    
    return render(request, 'accounts/admin/tours/image_form.html', {
        'form': form,
        'tour': tour,
        'image': image,
        'title': 'Edit Image'
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_tourimage')
def tour_image_delete(request, tour_id, image_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    image = get_object_or_404(TourImage, pk=image_id, tour=tour)
    
    if request.method == 'POST':
        try:
            image.delete()
            messages.success(request, 'Image deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting image: {str(e)}')
        return redirect('tour_image_list', tour_id=tour_id)
    
    return render(request, 'accounts/admin/tours/image_delete_confirm.html', {
        'tour': tour,
        'image': image
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tourimage')
def tour_image_set_primary(request, tour_id, image_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    image = get_object_or_404(TourImage, pk=image_id, tour=tour)
    
    if request.method == 'POST':
        try:
            # Remove primary from all images for this tour
            tour.images.all().update(is_primary=False)
            # Set this image as primary
            image.is_primary = True
            image.save()
            messages.success(request, 'Image set as primary!')
        except Exception as e:
            messages.error(request, f'Error setting primary image: {str(e)}')
        return redirect('tour_image_list', tour_id=tour_id)
    
    return render(request, 'accounts/admin/tours/image_set_primary_confirm.html', {
        'tour': tour,
        'image': image
    })


# Tour Highlight CRUD
@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_tourhighlight')
def tour_highlight_create(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    
    if request.method == 'POST':
        form = TourHighlightForm(request.POST)
        if form.is_valid():
            highlight = form.save(commit=False)
            highlight.tour = tour
            highlight.save()
            messages.success(request, 'Highlight added successfully!')
            return redirect('tour_highlights_list', tour_id=tour_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TourHighlightForm()
    
    return render(request, 'accounts/admin/tours/highlight_form.html', {
        'form': form,
        'tour': tour,
        'title': 'Add Highlight'
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tourhighlight')
def tour_highlight_edit(request, tour_id, highlight_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    highlight = get_object_or_404(TourHighlight, pk=highlight_id, tour=tour)
    
    if request.method == 'POST':
        form = TourHighlightForm(request.POST, instance=highlight)
        if form.is_valid():
            form.save()
            messages.success(request, 'Highlight updated successfully!')
            return redirect('tour_highlights_list', tour_id=tour_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TourHighlightForm(instance=highlight)
    
    return render(request, 'accounts/admin/tours/highlight_form.html', {
        'form': form,
        'tour': tour,
        'highlight': highlight,
        'title': 'Edit Highlight'
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_tourhighlight')
def tour_highlight_delete(request, tour_id, highlight_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    highlight = get_object_or_404(TourHighlight, pk=highlight_id, tour=tour)
    
    if request.method == 'POST':
        try:
            highlight.delete()
            messages.success(request, 'Highlight deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting highlight: {str(e)}')
        return redirect('tour_highlights_list', tour_id=tour_id)
    
    return render(request, 'accounts/admin/tours/highlight_delete_confirm.html', {
        'tour': tour,
        'highlight': highlight
    })


# Tour Included CRUD
@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tourincluded')
def tour_included_list(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    included_items = tour.included_items.all().order_by('display_order')
    return render(request, 'accounts/admin/tours/included_list.html', {'tour': tour, 'included_items': included_items})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_tourincluded')
def tour_included_create(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = TourIncludedForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.tour = tour
            item.save()
            messages.success(request, 'Included item added successfully!')
            return redirect('tour_included_list', tour_id=tour_id)
    else:
        form = TourIncludedForm()
    return render(request, 'accounts/admin/tours/included_form.html', {'form': form, 'tour': tour, 'title': 'Add Included Item'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tourincluded')
def tour_included_edit(request, tour_id, item_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    item = get_object_or_404(TourIncluded, pk=item_id, tour=tour)
    if request.method == 'POST':
        form = TourIncludedForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Included item updated successfully!')
            return redirect('tour_included_list', tour_id=tour_id)
    else:
        form = TourIncludedForm(instance=item)
    return render(request, 'accounts/admin/tours/included_form.html', {'form': form, 'tour': tour, 'item': item, 'title': 'Edit Included Item'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_tourincluded')
def tour_included_delete(request, tour_id, item_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    item = get_object_or_404(TourIncluded, pk=item_id, tour=tour)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Included item deleted successfully!')
        return redirect('tour_included_list', tour_id=tour_id)
    return render(request, 'accounts/admin/tours/included_delete_confirm.html', {'tour': tour, 'item': item})


# Tour Excluded CRUD
@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tourexcluded')
def tour_excluded_list(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    excluded_items = tour.excluded_items.all().order_by('display_order')
    return render(request, 'accounts/admin/tours/excluded_list.html', {'tour': tour, 'excluded_items': excluded_items})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_tourexcluded')
def tour_excluded_create(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = TourExcludedForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.tour = tour
            item.save()
            messages.success(request, 'Excluded item added successfully!')
            return redirect('tour_excluded_list', tour_id=tour_id)
    else:
        form = TourExcludedForm()
    return render(request, 'accounts/admin/tours/excluded_form.html', {'form': form, 'tour': tour, 'title': 'Add Excluded Item'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tourexcluded')
def tour_excluded_edit(request, tour_id, item_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    item = get_object_or_404(TourExcluded, pk=item_id, tour=tour)
    if request.method == 'POST':
        form = TourExcludedForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Excluded item updated successfully!')
            return redirect('tour_excluded_list', tour_id=tour_id)
    else:
        form = TourExcludedForm(instance=item)
    return render(request, 'accounts/admin/tours/excluded_form.html', {'form': form, 'tour': tour, 'item': item, 'title': 'Edit Excluded Item'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_tourexcluded')
def tour_excluded_delete(request, tour_id, item_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    item = get_object_or_404(TourExcluded, pk=item_id, tour=tour)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Excluded item deleted successfully!')
        return redirect('tour_excluded_list', tour_id=tour_id)
    return render(request, 'accounts/admin/tours/excluded_delete_confirm.html', {'tour': tour, 'item': item})


# Tour Itinerary CRUD
@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_touritinerary')
def tour_itinerary_list(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    itinerary_steps = tour.itinerary_steps.all().order_by('step_number')
    return render(request, 'accounts/admin/tours/itinerary_list.html', {'tour': tour, 'itinerary_steps': itinerary_steps})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_touritinerary')
def tour_itinerary_create(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = TourItineraryForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            step.tour = tour
            step.save()
            messages.success(request, 'Itinerary step added successfully!')
            return redirect('tour_itinerary_list', tour_id=tour_id)
    else:
        form = TourItineraryForm()
    return render(request, 'accounts/admin/tours/itinerary_form.html', {'form': form, 'tour': tour, 'title': 'Add Itinerary Step'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_touritinerary')
def tour_itinerary_edit(request, tour_id, step_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    step = get_object_or_404(TourItinerary, pk=step_id, tour=tour)
    if request.method == 'POST':
        form = TourItineraryForm(request.POST, instance=step)
        if form.is_valid():
            form.save()
            messages.success(request, 'Itinerary step updated successfully!')
            return redirect('tour_itinerary_list', tour_id=tour_id)
    else:
        form = TourItineraryForm(instance=step)
    return render(request, 'accounts/admin/tours/itinerary_form.html', {'form': form, 'tour': tour, 'step': step, 'title': 'Edit Itinerary Step'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_touritinerary')
def tour_itinerary_delete(request, tour_id, step_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    step = get_object_or_404(TourItinerary, pk=step_id, tour=tour)
    if request.method == 'POST':
        step.delete()
        messages.success(request, 'Itinerary step deleted successfully!')
        return redirect('tour_itinerary_list', tour_id=tour_id)
    return render(request, 'accounts/admin/tours/itinerary_delete_confirm.html', {'tour': tour, 'step': step})


# Tour Requirement CRUD
@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tourrequirement')
def tour_requirement_list(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    requirements = tour.requirements.all().order_by('display_order')
    return render(request, 'accounts/admin/tours/requirement_list.html', {'tour': tour, 'requirements': requirements})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_tourrequirement')
def tour_requirement_create(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = TourRequirementForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.tour = tour
            req.save()
            messages.success(request, 'Requirement added successfully!')
            return redirect('tour_requirement_list', tour_id=tour_id)
    else:
        form = TourRequirementForm()
    return render(request, 'accounts/admin/tours/requirement_form.html', {'form': form, 'tour': tour, 'title': 'Add Requirement'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tourrequirement')
def tour_requirement_edit(request, tour_id, req_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    req = get_object_or_404(TourRequirement, pk=req_id, tour=tour)
    if request.method == 'POST':
        form = TourRequirementForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, 'Requirement updated successfully!')
            return redirect('tour_requirement_list', tour_id=tour_id)
    else:
        form = TourRequirementForm(instance=req)
    return render(request, 'accounts/admin/tours/requirement_form.html', {'form': form, 'tour': tour, 'req': req, 'title': 'Edit Requirement'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_tourrequirement')
def tour_requirement_delete(request, tour_id, req_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    req = get_object_or_404(TourRequirement, pk=req_id, tour=tour)
    if request.method == 'POST':
        req.delete()
        messages.success(request, 'Requirement deleted successfully!')
        return redirect('tour_requirement_list', tour_id=tour_id)
    return render(request, 'accounts/admin/tours/requirement_delete_confirm.html', {'tour': tour, 'req': req})


# Tour FAQ CRUD
@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tourfaq')
def tour_faq_list(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    faqs = tour.faqs.all().order_by('display_order')
    return render(request, 'accounts/admin/tours/faq_list.html', {'tour': tour, 'faqs': faqs})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_tourfaq')
def tour_faq_create(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = TourFAQForm(request.POST)
        if form.is_valid():
            faq = form.save(commit=False)
            faq.tour = tour
            faq.save()
            messages.success(request, 'FAQ added successfully!')
            return redirect('tour_faq_list', tour_id=tour_id)
    else:
        form = TourFAQForm()
    return render(request, 'accounts/admin/tours/faq_form.html', {'form': form, 'tour': tour, 'title': 'Add FAQ'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tourfaq')
def tour_faq_edit(request, tour_id, faq_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    faq = get_object_or_404(TourFAQ, pk=faq_id, tour=tour)
    if request.method == 'POST':
        form = TourFAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, 'FAQ updated successfully!')
            return redirect('tour_faq_list', tour_id=tour_id)
    else:
        form = TourFAQForm(instance=faq)
    return render(request, 'accounts/admin/tours/faq_form.html', {'form': form, 'tour': tour, 'faq': faq, 'title': 'Edit FAQ'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_tourfaq')
def tour_faq_delete(request, tour_id, faq_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    faq = get_object_or_404(TourFAQ, pk=faq_id, tour=tour)
    if request.method == 'POST':
        faq.delete()
        messages.success(request, 'FAQ deleted successfully!')
        return redirect('tour_faq_list', tour_id=tour_id)
    return render(request, 'accounts/admin/tours/faq_delete_confirm.html', {'tour': tour, 'faq': faq})


# Tour Pricing CRUD
@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tourpricing')
def tour_pricing_list(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    pricing_options = tour.pricing_options.all()
    return render(request, 'accounts/admin/tours/pricing_list.html', {'tour': tour, 'pricing_options': pricing_options})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_tourpricing')
def tour_pricing_create(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = TourPricingForm(request.POST)
        if form.is_valid():
            pricing = form.save(commit=False)
            pricing.tour = tour
            pricing.save()
            messages.success(request, 'Pricing option added successfully!')
            return redirect('tour_pricing_list', tour_id=tour_id)
    else:
        form = TourPricingForm()
    return render(request, 'accounts/admin/tours/pricing_form.html', {'form': form, 'tour': tour, 'title': 'Add Pricing Option'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tourpricing')
def tour_pricing_edit(request, tour_id, pricing_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    pricing = get_object_or_404(TourPricing, pk=pricing_id, tour=tour)
    if request.method == 'POST':
        form = TourPricingForm(request.POST, instance=pricing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pricing option updated successfully!')
            return redirect('tour_pricing_list', tour_id=tour_id)
    else:
        form = TourPricingForm(instance=pricing)
    return render(request, 'accounts/admin/tours/pricing_form.html', {'form': form, 'tour': tour, 'pricing': pricing, 'title': 'Edit Pricing Option'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_tourpricing')
def tour_pricing_delete(request, tour_id, pricing_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    pricing = get_object_or_404(TourPricing, pk=pricing_id, tour=tour)
    if request.method == 'POST':
        pricing.delete()
        messages.success(request, 'Pricing option deleted successfully!')
        return redirect('tour_pricing_list', tour_id=tour_id)
    return render(request, 'accounts/admin/tours/pricing_delete_confirm.html', {'tour': tour, 'pricing': pricing})


# Tour Schedule CRUD
@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tourschedule')
def tour_schedule_list(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    schedules = tour.schedules.all().order_by('date', 'start_time')
    return render(request, 'accounts/admin/tours/schedule_list.html', {'tour': tour, 'schedules': schedules})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_tourschedule')
def tour_schedule_create(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = TourScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.tour = tour
            schedule.save()
            messages.success(request, 'Schedule added successfully!')
            return redirect('tour_schedule_list', tour_id=tour_id)
    else:
        form = TourScheduleForm()
    return render(request, 'accounts/admin/tours/schedule_form.html', {'form': form, 'tour': tour, 'title': 'Add Schedule'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tourschedule')
def tour_schedule_edit(request, tour_id, schedule_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    schedule = get_object_or_404(TourSchedule, pk=schedule_id, tour=tour)
    if request.method == 'POST':
        form = TourScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule updated successfully!')
            return redirect('tour_schedule_list', tour_id=tour_id)
    else:
        form = TourScheduleForm(instance=schedule)
    return render(request, 'accounts/admin/tours/schedule_form.html', {'form': form, 'tour': tour, 'schedule': schedule, 'title': 'Edit Schedule'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_tourschedule')
def tour_schedule_delete(request, tour_id, schedule_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    schedule = get_object_or_404(TourSchedule, pk=schedule_id, tour=tour)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully!')
        return redirect('tour_schedule_list', tour_id=tour_id)
    return render(request, 'accounts/admin/tours/schedule_delete_confirm.html', {'tour': tour, 'schedule': schedule})


# Tour Blackout Date CRUD
@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_tourblackoutdate')
def tour_blackout_list(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    blackout_dates = tour.blackout_dates.all().order_by('start_date')
    return render(request, 'accounts/admin/tours/blackout_list.html', {'tour': tour, 'blackout_dates': blackout_dates})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_tourblackoutdate')
def tour_blackout_create(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = TourBlackoutDateForm(request.POST)
        if form.is_valid():
            blackout = form.save(commit=False)
            blackout.tour = tour
            blackout.save()
            messages.success(request, 'Blackout date added successfully!')
            return redirect('tour_blackout_list', tour_id=tour_id)
    else:
        form = TourBlackoutDateForm()
    return render(request, 'accounts/admin/tours/blackout_form.html', {'form': form, 'tour': tour, 'title': 'Add Blackout Date'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tourblackoutdate')
def tour_blackout_edit(request, tour_id, blackout_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    blackout = get_object_or_404(TourBlackoutDate, pk=blackout_id, tour=tour)
    if request.method == 'POST':
        form = TourBlackoutDateForm(request.POST, instance=blackout)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blackout date updated successfully!')
            return redirect('tour_blackout_list', tour_id=tour_id)
    else:
        form = TourBlackoutDateForm(instance=blackout)
    return render(request, 'accounts/admin/tours/blackout_form.html', {'form': form, 'tour': tour, 'blackout': blackout, 'title': 'Edit Blackout Date'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_tourblackoutdate')
def tour_blackout_delete(request, tour_id, blackout_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    blackout = get_object_or_404(TourBlackoutDate, pk=blackout_id, tour=tour)
    if request.method == 'POST':
        blackout.delete()
        messages.success(request, 'Blackout date deleted successfully!')
        return redirect('tour_blackout_list', tour_id=tour_id)
    return render(request, 'accounts/admin/tours/blackout_delete_confirm.html', {'tour': tour, 'blackout': blackout})
