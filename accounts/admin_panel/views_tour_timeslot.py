from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from accounts.models import Tour, TimeSlot, TourTimeSlot
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_tour')
def tour_timeslot_select(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    timeslots = TimeSlot.objects.all().order_by('name')
    
    # Get IDs of timeslots currently associated with this tour
    current_timeslot_ids = set(
        TourTimeSlot.objects.filter(tour=tour).values_list('time_slot_id', flat=True)
    )
    
    if request.method == 'POST':
        selected_ids = request.POST.getlist('timeslot_ids')
        # Convert selected IDs to a set of integers
        selected_ids = {int(tid) for tid in selected_ids if tid.isdigit()}
        
        # Determine IDs to add and remove
        to_add = selected_ids - current_timeslot_ids
        to_remove = current_timeslot_ids - selected_ids
        
        # Delete unselected ones
        TourTimeSlot.objects.filter(tour=tour, time_slot_id__in=to_remove).delete()
        
        # Add newly selected ones
        new_mappings = [
            TourTimeSlot(tour=tour, time_slot_id=tid) for tid in to_add
        ]
        if new_mappings:
            TourTimeSlot.objects.bulk_create(new_mappings)
            
        messages.success(request, f'Time slots for tour "{tour.title}" updated successfully!')
        return redirect('tour_list')
        
    return render(request, 'accounts/admin/timeslot/select.html', {
        'tour': tour,
        'timeslots': timeslots,
        'current_timeslot_ids': current_timeslot_ids,
        'title': f'Select Time Slots for {tour.title}'
    })
