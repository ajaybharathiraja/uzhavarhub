import os
import django
import random
import pandas as pd
from django.utils import timezone
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uzhavarhub.settings')
django.setup()

from django.contrib.auth import get_user_model
from marketplace.models import Product
from orders.models import Order, OrderItem
from accounts.models import CustomerProfile

User = get_user_model()

def generate_real_sales():
    print("Generating sales from real dataset...")
    customer, _ = User.objects.get_or_create(username='dataset_customer', defaults={
        'email': 'customer@example.com',
        'role': 'CUSTOMER'
    })
    CustomerProfile.objects.get_or_create(user=customer)
    
    products = list(Product.objects.all())
    if not products:
        print("No products found! Run populate_db.py first.")
        return

    # Load real ecommerce dataset
    df = pd.read_csv('data/processed/ecommerce_sales.csv')
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df = df.dropna(subset=['order_date']).head(500) # Load 500 real transactions
    
    for _, row in df.iterrows():
        order_date = row['order_date']
        # Convert to timezone aware datetime
        order_date = timezone.make_aware(order_date) if timezone.is_naive(order_date) else order_date
        
        order = Order.objects.create(
            customer=customer,
            status='COMPLETED'
        )
        Order.objects.filter(id=order.id).update(created_at=order_date)
        
        product = random.choice(products)
        qty = int(row['quantity']) if pd.notna(row['quantity']) else random.randint(1, 5)
        price = float(row['unit_price']) if pd.notna(row['unit_price']) else product.price
        
        total_amount = price * qty
        
        OrderItem.objects.create(
            order=order,
            product=product,
            farmer=product.farmer.user,
            quantity=qty,
            price_at_purchase=price
        )
        
        Order.objects.filter(id=order.id).update(total_amount=total_amount)

    print(f"Successfully generated {len(df)} orders from real dataset!")

if __name__ == '__main__':
    generate_real_sales()
