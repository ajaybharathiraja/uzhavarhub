import os
import django
import pandas as pd
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uzhavarhub.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import FarmerProfile
from marketplace.models import Category, Product

User = get_user_model()

def populate():
    # 1. Create a sample farmer if it doesn't exist
    farmer, created = User.objects.get_or_create(username='sample_farmer', defaults={
        'email': 'farmer@example.com',
        'role': 'FARMER'
    })
    if created:
        farmer.set_password('farmer123')
        farmer.save()
        FarmerProfile.objects.get_or_create(user=farmer, defaults={'farm_name': 'Kaveri Delta Farms', 'location': 'Thanjavur, Tamil Nadu'})
        print("Created sample_farmer (password: farmer123)")
    else:
        FarmerProfile.objects.get_or_create(user=farmer, defaults={'farm_name': 'Kaveri Delta Farms', 'location': 'Thanjavur, Tamil Nadu'})

    # 2. Extract real crops from dataset
    print("Loading real crops from dataset...")
    df = pd.read_csv('data/raw/crop_recommendation.csv')
    unique_crops = df['label'].unique()
    
    # 3. Create Categories
    categories_data = [
        {'name': 'Realtime Fruits', 'slug': 'realtime-fruits', 'description': 'Fruits from dataset.'},
        {'name': 'Realtime Grains & Pulses', 'slug': 'realtime-grains', 'description': 'Grains and pulses from dataset.'},
        {'name': 'Realtime Cash Crops', 'slug': 'realtime-cash-crops', 'description': 'Cash crops from dataset.'}
    ]
    
    cat_objs = {}
    for c_data in categories_data:
        cat, _ = Category.objects.get_or_create(slug=c_data['slug'], defaults=c_data)
        cat_objs[c_data['slug']] = cat

    # 4. Create sample Products from real crops
    for crop in unique_crops:
        if crop in ['apple', 'banana', 'grapes', 'mango', 'muskmelon', 'orange', 'papaya', 'pomegranate', 'watermelon', 'coconut']:
            cat = cat_objs['realtime-fruits']
        elif crop in ['cotton', 'jute', 'coffee']:
            cat = cat_objs['realtime-cash-crops']
        else:
            cat = cat_objs['realtime-grains']
            
        Product.objects.get_or_create(
            slug=f'real-{crop}',
            defaults={
                'farmer': farmer.farmer_profile,
                'category': cat,
                'name': crop.capitalize(),
                'description': f'Real {crop} cultivated locally.',
                'price': round(random.uniform(30.0, 300.0), 2),
                'unit': 'kg',
                'stock_quantity': random.randint(100, 1000)
            }
        )
        print(f"Ensured real product: {crop.capitalize()}")

    print("Successfully populated the database with real dataset products!")

if __name__ == '__main__':
    populate()
