from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def permission_required_with_message(perm, redirect_url='admin_dashboard'):
    """
    Custom permission decorator that redirects to dashboard with error message
    instead of showing 403 page.
    
    Usage:
        @permission_required_with_message('accounts.view_country')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if user has the permission
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)
            else:
                # User doesn't have permission - redirect with message
                messages.error(request, f'You do not have permission to access this module.')
                return redirect(redirect_url)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """
    Decorator to check if user is staff/admin before accessing view
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'You must be an admin to access this page.')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
