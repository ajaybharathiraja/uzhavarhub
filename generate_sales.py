import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uzhavarhub.settings')
django.setup()

from django.contrib.auth import get_user_model
from marketplace.models import Product
from orders.models import Order, OrderItem
from accounts.models import CustomerProfile

User = get_user_model()

def generate_mock_sales():
    print("Generating mock sales data...")
    # Create a dummy customer
    customer, _ = User.objects.get_or_create(username='dummy_customer', defaults={
        'email': 'customer@example.com',
        'role': 'CUSTOMER'
    })
    CustomerProfile.objects.get_or_create(user=customer)
    
    products = list(Product.objects.all())
    if not products:
        print("No products found! Run populate_db.py first.")
        return

    now = timezone.now()
    
    # Generate 500 dummy orders over the last 90 days
    for _ in range(500):
        # Random date in last 90 days
        days_ago = random.randint(0, 90)
        order_date = now - timedelta(days=days_ago, hours=random.randint(0,23))
        
        order = Order.objects.create(
            customer=customer,
            status='COMPLETED'
        )
        # Override auto_now_add for mock data
        Order.objects.filter(id=order.id).update(created_at=order_date)
        
        # Add 1 to 3 items per order
        total_amount = 0
        for _ in range(random.randint(1, 3)):
            product = random.choice(products)
            # Make Alphonso Mangoes and Tomatoes sell faster by increasing their random weight/quantity
            qty = random.randint(1, 5)
            if 'Tomato' in product.name or 'Mango' in product.name:
                qty = random.randint(3, 10)
                
            price = product.price
            total_amount += (price * qty)
            
            OrderItem.objects.create(
                order=order,
                product=product,
                farmer=product.farmer.user,
                quantity=qty,
                price_at_purchase=price
            )
        
        Order.objects.filter(id=order.id).update(total_amount=total_amount)

    print("Successfully generated 500 mock orders!")

if __name__ == '__main__':
    generate_mock_sales()
