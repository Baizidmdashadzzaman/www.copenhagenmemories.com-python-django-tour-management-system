from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import TeamMember
from .forms import TeamMemberForm
from .decorators import permission_required_with_message

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.view_teammember')
def team_member_list(request):
    search_query = request.GET.get('search', '')
    team_members = TeamMember.objects.all()
    
    if search_query:
        team_members = team_members.filter(
            Q(name__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    paginator = Paginator(team_members, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/team/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.add_teammember')
def team_member_create(request):
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Team member added successfully!')
                return redirect('team_member_list')
            except Exception as e:
                messages.error(request, f'Error adding team member: {str(e)}')
    else:
        form = TeamMemberForm()
    
    return render(request, 'accounts/admin/team/form.html', {
        'form': form,
        'title': 'Add Team Member'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.change_teammember')
def team_member_edit(request, pk):
    team_member = get_object_or_404(TeamMember, pk=pk)
    
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=team_member)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Team member updated successfully!')
                return redirect('team_member_list')
            except Exception as e:
                messages.error(request, f'Error updating team member: {str(e)}')
    else:
        form = TeamMemberForm(instance=team_member)
    
    return render(request, 'accounts/admin/team/form.html', {
        'form': form,
        'team_member': team_member,
        'title': 'Edit Team Member'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required_with_message('accounts.delete_teammember')
def team_member_delete(request, pk):
    team_member = get_object_or_404(TeamMember, pk=pk)
    team_member.delete()
    messages.success(request, 'Team member deleted successfully!')
    return redirect('team_member_list')
