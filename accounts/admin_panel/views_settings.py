from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from accounts.models import SiteSetting
from .forms import SiteSettingForm

@login_required
@user_passes_test(lambda u: u.is_staff)
def site_settings(request):
    settings = SiteSetting.get_settings()
    
    if request.method == 'POST':
        form = SiteSettingForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site settings updated successfully!')
            return redirect('site_settings')
    else:
        form = SiteSettingForm(instance=settings)
    
    return render(request, 'accounts/admin/settings.html', {
        'form': form,
        'settings': settings
    })
