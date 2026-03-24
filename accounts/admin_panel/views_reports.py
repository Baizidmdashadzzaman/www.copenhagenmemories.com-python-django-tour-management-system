from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from accounts.models import SiteSetting
from .forms import SiteSettingForm

@login_required
@user_passes_test(lambda u: u.is_staff)
def reports_list(request):
    
    return render(request, 'accounts/admin/reports/reports_list.html')
