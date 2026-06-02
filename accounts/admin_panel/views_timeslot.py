from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import TimeSlot
from .forms import TimeSlotForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_timeslot')
def timeslot_list(request):
    search_query = request.GET.get('search', '')
    timeslots = TimeSlot.objects.all()
    
    if search_query:
        timeslots = timeslots.filter(
            Q(name__icontains=search_query) 
        )
    
    paginator = Paginator(timeslots, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/timeslot/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_timeslot')
def timeslot_create(request):
    if request.method == 'POST':
        form = TimeSlotForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Time Slot added successfully!')
                return redirect('timeslot_list')
            except Exception as e:
                messages.error(request, f'Error adding Time Slot: {str(e)}')
    else:
        form = TimeSlotForm()
    
    return render(request, 'accounts/admin/timeslot/form.html', {
        'form': form,
        'title': 'Add Time Slot'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_timeslot')
def timeslot_edit(request, pk):
    timeslot = get_object_or_404(TimeSlot, pk=pk)
    
    if request.method == 'POST':
        form = TimeSlotForm(request.POST, request.FILES, instance=timeslot)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Time Slot updated successfully!')
                return redirect('timeslot_list')
            except Exception as e:
                messages.error(request, f'Error updating Time Slot: {str(e)}')
    else:
        form = TimeSlotForm(instance=timeslot)
    
    return render(request, 'accounts/admin/timeslot/form.html', {
        'form': form,
        'timeslot': timeslot,
        'title': 'Edit Time Slot'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_timeslot')
def timeslot_delete(request, pk):
    timeslot = get_object_or_404(TimeSlot, pk=pk)
    timeslot.delete()
    messages.success(request, 'Time Slot deleted successfully!')
    return redirect('timeslot_list')
