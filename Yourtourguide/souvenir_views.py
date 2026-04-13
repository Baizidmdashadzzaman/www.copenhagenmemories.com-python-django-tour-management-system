import random
import string
import requests
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from accounts.models import Souvenir, SouvenirOrder, SouvenirOrderItem, Customer
from .forms import SouvenirOrderForm
from django.core.mail import send_mail
import logging
logger = logging.getLogger(__name__)

def souvenirs_list(request):
    search_query = request.GET.get('search', '')
    souvenirs_list = Souvenir.objects.filter(status='active')
    
    if search_query:
        souvenirs_list = souvenirs_list.filter(
            Q(title__icontains=search_query) |
            Q(title_dk__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(description_dk__icontains=search_query)
        )
        
    paginator = Paginator(souvenirs_list, 12)
    page_number = request.GET.get('page')
    souvenirs = paginator.get_page(page_number)
    
    context = {
        'souvenirs': souvenirs,
        'search_query': search_query,
        'total_souvenirs': souvenirs_list.count()
    }
    return render(request, 'frontend/pages/souvenirs/souvenirs_list.html', context)

def souvenir_detail(request, souvenir_id):
    if isinstance(souvenir_id, str):
        souvenir_id = int(souvenir_id.split('-')[-1])
    else:
        souvenir_id = int(souvenir_id)
        
    souvenir = get_object_or_404(Souvenir, pk=souvenir_id, status='active')
    
    # Get related souvenirs (same status, excluding current)
    related_souvenirs = Souvenir.objects.filter(status='active').exclude(pk=souvenir_id)[:4]
    
    context = {
        'souvenir': souvenir,
        'related_souvenirs': related_souvenirs
    }
    return render(request, 'frontend/pages/souvenirs/souvenirs_detail.html', context)

# Cart Functionality
def add_to_cart(request, souvenir_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        souvenir = get_object_or_404(Souvenir, id=souvenir_id)
        
        cart = request.session.get('cart', {})
        
        souvenir_id_str = str(souvenir_id)
        if souvenir_id_str in cart:
            cart[souvenir_id_str]['quantity'] += quantity
        else:
            cart[souvenir_id_str] = {
                'title': souvenir.title,
                'price': float(souvenir.price),
                'image': souvenir.image.url if souvenir.image else '',
                'quantity': quantity
            }
            
        request.session['cart'] = cart
        messages.success(request, f'Added {souvenir.title} to cart.')
        
    return redirect(request.META.get('HTTP_REFERER', 'souvenirs_list_frontend'))

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for item_id, item_data in cart.items():
        subtotal = item_data['price'] * item_data['quantity']
        total_price += subtotal
        cart_items.append({
            'id': item_id,
            'title': item_data['title'],
            'price': item_data['price'],
            'image': item_data['image'],
            'quantity': item_data['quantity'],
            'subtotal': subtotal
        })
        
    order_form = SouvenirOrderForm()
    
    # Pre-fill if user is logged in
    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        customer = request.user.customer_profile
        order_form = SouvenirOrderForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': customer.phone,
            'address': customer.address,
        })

    if request.method == 'POST' and 'submit_order' in request.POST:
        order_form = SouvenirOrderForm(request.POST)
        if order_form.is_valid():
            if not cart:
                messages.error(request, "Your cart is empty.")
                return redirect('cart_view')
                
            order = order_form.save(commit=False)
            
            # Generate order number
            order.order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            order.total_amount = total_price
            
            if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
                order.customer = request.user.customer_profile
                
            order.save()
            
            # Create order items
            for item_id, item_data in cart.items():
                souvenir = Souvenir.objects.get(id=item_id)
                SouvenirOrderItem.objects.create(
                    order=order,
                    souvenir=souvenir,
                    price=item_data['price'],
                    quantity=item_data['quantity']
                )

            if getattr(settings, 'USE_PAYMENT_GATEWAY', False):
                api_key = getattr(settings, 'FLATPAY_KEY', '')
                url = 'https://checkout-api.frisbii.com/v1/session/charge'
                
                amount = int(float(total_price) * 100)
                accept_url = request.build_absolute_uri(reverse('cart_payment_accept', args=[order.order_number]))
                cancel_url = request.build_absolute_uri(reverse('cart_payment_cancel', args=[order.order_number]))
                
                data = {
                    'order': {
                        'handle': order.order_number,
                        'amount': amount,
                        'currency': 'USD',
                        'customer': {
                            'email': order.email,
                            'first_name': order.first_name,
                            'last_name': order.last_name,
                        }
                    },
                    'accept_url': accept_url,
                    'cancel_url': cancel_url
                }
                
                try:
                    response = requests.post(url, auth=(api_key, ''), json=data)
                    response_data = response.json()
                    if 'url' in response_data:
                        return redirect(response_data['url'])
                    else:
                        messages.error(request, f"Payment gateway error: {response_data.get('error', 'Unknown error')}")
                        return redirect('cart_view')
                except Exception as e:
                    messages.error(request, f"Payment gateway error: {str(e)}")
                    return redirect('cart_view')
            else:
                # Original flow
                for item_id, item_data in cart.items():
                    souvenir = Souvenir.objects.get(id=item_id)
                    souvenir.stock -= item_data['quantity']
                    souvenir.save()
                    
                request.session['cart'] = {}
                messages.success(request, "Order placed successfully!")
                return render(request, 'frontend/pages/cart/order_confirmation.html', {'order': order})

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'order_form': order_form
    }
    return render(request, 'frontend/pages/cart/cart.html', context)

def update_cart(request, souvenir_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        
        souvenir_id_str = str(souvenir_id)
        if souvenir_id_str in cart:
            if quantity > 0:
                cart[souvenir_id_str]['quantity'] = quantity
            else:
                del cart[souvenir_id_str]
            request.session['cart'] = cart
            messages.success(request, 'Cart updated.')
            
    return redirect('cart_view')

def remove_from_cart(request, souvenir_id):
    cart = request.session.get('cart', {})
    souvenir_id_str = str(souvenir_id)
    
    if souvenir_id_str in cart:
        del cart[souvenir_id_str]
        request.session['cart'] = cart
        messages.success(request, 'Item removed from cart.')
        
    return redirect('cart_view')

def cart_payment_accept(request, order_number):
    order = get_object_or_404(SouvenirOrder, order_number=order_number)
    
    if getattr(settings, 'USE_PAYMENT_GATEWAY', False):
        api_key = getattr(settings, 'FLATPAY_KEY', '')
        url = f"https://api.frisbii.com/v1/charge/{order_number}"
        try:
            response = requests.get(url, auth=(api_key, ''), headers={'Accept': 'application/json'})
            data = response.json()
            if response.status_code == 200 and data.get('state') not in ['authorized', 'settled']:
                messages.error(request, "Payment was not authorized.")
                return redirect('cart_view')
        except Exception as e:
            pass

    if order.status != 'confirmed':
        order.status = 'confirmed'
        order.save()
        
        for item in order.items.all():
            souvenir = item.souvenir
            if souvenir:
                souvenir.stock -= item.quantity
                souvenir.save()

    request.session['cart'] = {}

    try:
        send_mail(
            'New Souvenir Order',
            f'Booking Number: {souvenir.order_number}',
            settings.DEFAULT_FROM_EMAIL,
            ['contact@copenhagenmemories.com'],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Admin email failed: {str(e)}")

    messages.success(request, "Order placed successfully!")
    return render(request, 'frontend/pages/cart/order_confirmation.html', {'order': order})

def cart_payment_cancel(request, order_number):
    order = get_object_or_404(SouvenirOrder, order_number=order_number)
    if order.status != 'confirmed':
        order.status = 'cancelled'
        order.save()
    messages.warning(request, "Payment was cancelled.")
    return redirect('cart_view')
