from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import Newsletter
from django.views.decorators.http import require_POST

@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email')
    if email:
        if Newsletter.objects.filter(email=email).exists():
            messages.warning(request, 'You are already subscribed to our newsletter.')
        else:
            Newsletter.objects.create(email=email)
            messages.success(request, 'Successfully subscribed to our newsletter!')
    else:
        messages.error(request, 'Please provide a valid email address.')
    
    return redirect(request.META.get('HTTP_REFERER', '/'))
