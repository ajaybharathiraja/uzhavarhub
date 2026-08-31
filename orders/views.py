from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from marketplace.models import Product
from .models import Cart, CartItem

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'orders/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = sum(item.quantity for item in cart.items.all())
        return JsonResponse({'success': True, 'message': f'Added {product.name}', 'cart_count': cart_count})
        
    if not item_created:
        messages.success(request, f"Added another {product.name} to your cart.")
    else:
        messages.success(request, f"{product.name} was added to your cart.")
        
    # Redirect back to where they came from
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:product_list'))

@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('orders:view_cart')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('marketplace:product_list')
        
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        
        if not shipping_address:
            messages.error(request, "Please provide a shipping address.")
            return redirect('orders:checkout')
            
        # Create Order
        order = Order.objects.create(
            customer=request.user,
            total_amount=cart.total_price + 40, # Add fixed 40 for delivery
            shipping_address=shipping_address,
            status='PLACED'
        )
        
        # Move items from Cart to Order
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                farmer=cart_item.product.farmer,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.product.price
            )
            
        # Empty the cart
        cart.items.all().delete()
        
        return redirect('payments:process', order_id=order.id)
        
    return render(request, 'orders/checkout.html', {'cart': cart})

@login_required
def order_success(request, order_id):
    from .models import Order
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'orders/success.html', {'order': order})

@login_required
def customer_orders(request):
    from .models import Order
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'orders/history.html', {'orders': orders})
