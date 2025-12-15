from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import AdminUserForm
from django.core.paginator import Paginator
from django.db.models import Q
from .decorators import permission_required_with_message

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
@permission_required_with_message('auth.view_user')
def admin_list(request):
    query = request.GET.get('q')
    admins = User.objects.filter(is_staff=True).order_by('-date_joined')
    
    if query:
        admins = admins.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    paginator = Paginator(admins, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/admins/list.html', {'page_obj': page_obj, 'query': query})

@login_required
@user_passes_test(is_admin)
@permission_required_with_message('auth.add_user')
def admin_create(request):
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True # Ensure created user is staff
            user.save()
            form.save_m2m() # Save groups and permissions
            messages.success(request, 'Admin user created successfully!')
            return redirect('admin_list')
    else:
        form = AdminUserForm()
    
    return render(request, 'accounts/admin/admins/form.html', {'form': form, 'title': 'Create Admin'})

@login_required
@user_passes_test(is_admin)
@permission_required_with_message('auth.change_user')
def admin_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Admin user updated successfully!')
            return redirect('admin_list')
    else:
        form = AdminUserForm(instance=user)
    
    return render(request, 'accounts/admin/admins/form.html', {'form': form, 'title': 'Edit Admin'})

@login_required
@user_passes_test(is_admin)
@permission_required_with_message('auth.delete_user')
def admin_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, 'You cannot delete yourself!')
        else:
            user.delete()
            messages.success(request, 'Admin user deleted successfully!')
        return redirect('admin_list')
    return render(request, 'accounts/admin/admins/confirm_delete.html', {'user': user})
