from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from .models import Transaction
import uuid

@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status != 'PLACED':
        messages.error(request, "This order has already been processed.")
        return redirect('orders:history')
        
    if request.method == 'POST':
        # Simulate successful payment
        txn, created = Transaction.objects.get_or_create(
            order=order,
            defaults={
                'total_amount': order.total_amount,
                'gateway_reference': f"tok_{uuid.uuid4().hex[:10]}"
            }
        )
        txn.status = 'COMPLETED'
        txn.save()
        
        # Update order status
        order.status = 'PAID'
        order.save()
        
        return redirect('payments:payment_success', order_id=order.id)
        
    return render(request, 'payments/gateway.html', {'order': order})

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'payments/success.html', {'order': order})
