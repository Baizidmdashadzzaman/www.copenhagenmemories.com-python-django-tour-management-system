from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib import messages
from .forms import GroupForm
from django.core.paginator import Paginator
from django.db.models import Q
from .decorators import permission_required_with_message

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
@permission_required_with_message('auth.view_group')
def group_list(request):
    query = request.GET.get('q')
    groups = Group.objects.all().order_by('name')
    
    if query:
        groups = groups.filter(name__icontains=query)
    
    paginator = Paginator(groups, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/groups/list.html', {'page_obj': page_obj, 'query': query})

@login_required
@user_passes_test(is_admin)
@permission_required_with_message('auth.add_group')
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group created successfully!')
            return redirect('group_list')
    else:
        form = GroupForm()
    
    return render(request, 'accounts/admin/groups/form.html', {'form': form, 'title': 'Create Group'})

@login_required
@user_passes_test(is_admin)
@permission_required_with_message('auth.change_group')
def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group updated successfully!')
            return redirect('group_list')
    else:
        form = GroupForm(instance=group)
    
    return render(request, 'accounts/admin/groups/form.html', {'form': form, 'title': 'Edit Group'})

@login_required
@user_passes_test(is_admin)
@permission_required_with_message('auth.delete_group')
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Group deleted successfully!')
        return redirect('group_list')
    return render(request, 'accounts/admin/groups/confirm_delete.html', {'group': group})
