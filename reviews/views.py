from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from marketplace.models import Product
from orders.models import OrderItem
from .models import Review

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        # Validation: Must be 1-5
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Invalid rating.")
            return redirect('marketplace:product_detail', slug=product.slug)
            
        # Validation: Must have bought it
        has_purchased = OrderItem.objects.filter(
            order__customer=request.user,
            product=product,
            order__status__in=['PAID', 'SHIPPED', 'DELIVERED', 'COMPLETED']
        ).exists()
        
        if not has_purchased:
            messages.error(request, "You can only review products you have purchased.")
            return redirect('marketplace:product_detail', slug=product.slug)
            
        # Create or update review
        review, created = Review.objects.update_or_create(
            product=product,
            customer=request.user,
            defaults={
                'rating': rating,
                'comment': comment
            }
        )
        
        messages.success(request, "Thank you for your review!")
        return redirect('marketplace:product_detail', slug=product.slug)
        
    return redirect('marketplace:product_detail', slug=product.slug)
