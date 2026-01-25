from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from accounts.models import Souvenir

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
        
    context = {
        'cart_items': cart_items,
        'total_price': total_price
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
