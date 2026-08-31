import os
import django

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
        FarmerProfile.objects.get_or_create(user=farmer, defaults={'farm_name': 'Green Valley Farms'})
        print("Created sample_farmer (password: farmer123)")
    else:
        # Just ensure profile exists
        FarmerProfile.objects.get_or_create(user=farmer, defaults={'farm_name': 'Green Valley Farms'})

    # 2. Create Categories
    categories_data = [
        {'name': 'Fresh Vegetables', 'slug': 'fresh-vegetables', 'description': 'Farm fresh organic vegetables.'},
        {'name': 'Fresh Fruits', 'slug': 'fresh-fruits', 'description': 'Seasonal fresh fruits.'},
        {'name': 'Dairy & Eggs', 'slug': 'dairy-eggs', 'description': 'Pure milk, cheese, and free-range eggs.'},
        {'name': 'Grains & Pulses', 'slug': 'grains-pulses', 'description': 'High quality grains directly from the farm.'}
    ]
    
    cat_objs = {}
    for c_data in categories_data:
        cat, _ = Category.objects.get_or_create(slug=c_data['slug'], defaults=c_data)
        cat_objs[c_data['slug']] = cat
        print(f"Ensured category: {cat.name}")

    # 3. Create sample Products
    products_data = [
        {
            'category': cat_objs['fresh-vegetables'], 'name': 'Organic Tomatoes', 'slug': 'organic-tomatoes',
            'description': 'Juicy, red organic tomatoes hand-picked this morning.',
            'price': 45.00, 'unit': 'kg', 'stock_quantity': 50
        },
        {
            'category': cat_objs['fresh-vegetables'], 'name': 'Fresh Spinach', 'slug': 'fresh-spinach',
            'description': 'Crisp and green spinach leaves, pesticide free.',
            'price': 20.00, 'unit': 'bunch', 'stock_quantity': 100
        },
        {
            'category': cat_objs['fresh-fruits'], 'name': 'Alphonso Mangoes', 'slug': 'alphonso-mangoes',
            'description': 'Sweet and ripe Alphonso mangoes, straight from the orchard.',
            'price': 400.00, 'unit': 'dozen', 'stock_quantity': 20
        },
        {
            'category': cat_objs['dairy-eggs'], 'name': 'Free-Range Eggs', 'slug': 'free-range-eggs',
            'description': 'Brown eggs from free-roaming hens.',
            'price': 90.00, 'unit': 'dozen', 'stock_quantity': 30
        },
        {
            'category': cat_objs['grains-pulses'], 'name': 'Basmati Rice', 'slug': 'basmati-rice',
            'description': 'Premium long-grain aged Basmati rice.',
            'price': 120.00, 'unit': 'kg', 'stock_quantity': 200
        }
    ]

    for p_data in products_data:
        Product.objects.get_or_create(
            slug=p_data['slug'],
            defaults={
                'farmer': farmer,
                'category': p_data['category'],
                'name': p_data['name'],
                'description': p_data['description'],
                'price': p_data['price'],
                'unit': p_data['unit'],
                'stock_quantity': p_data['stock_quantity']
            }
        )
        print(f"Ensured product: {p_data['name']}")

    print("Successfully populated the database with sample data!")

if __name__ == '__main__':
    populate()
