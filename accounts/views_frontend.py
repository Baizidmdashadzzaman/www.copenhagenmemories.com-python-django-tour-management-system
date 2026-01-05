from django.shortcuts import render, redirect
from accounts.forms import TourSupplierRegistrationForm, TourSupplierLoginForm
from django.contrib import messages
from accounts.models import Newsletter, TourSupplier
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

# def register_tour_supplier(request):
#     if request.method == 'POST':
#         form = TourSupplierRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Tour Supplier registration successful! You can now login.')
#             return redirect('login_tour_supplier')
#     else:
#         form = TourSupplierRegistrationForm()
    
#     return render(request, 'accounts/tour_supplier/register.html', {'form': form}) 

# def login_tour_supplier(request):
#     if request.method == 'POST':
#         form = TourSupplierLoginForm(request.POST)
#         if form.is_valid():
#             supplier = form.cleaned_data['supplier']
#             request.session['supplier_id'] = supplier.id
#             messages.success(request, 'Successfully logged in!')
#             return redirect('tour_supplier_dashboard')
#     else:
#         form = TourSupplierLoginForm()
    
#     return render(request, 'accounts/tour_supplier/login.html', {'form': form})


# def tour_supplier_dashboard(request):
#     supplier_id = request.session.get('supplier_id')
#     if not supplier_id:
#         messages.error(request, 'Please login first.')
#         return redirect('login_tour_supplier')
    
#     supplier = TourSupplier.objects.get(id=supplier_id)
#     return render(request, 'accounts/tour_supplier/dashboard.html', {'supplier': supplier})

# def logout_tour_supplier(request):
    if 'supplier_id' in request.session:
        del request.session['supplier_id']
    messages.success(request, 'Successfully logged out!')
    return redirect('login_tour_supplier')