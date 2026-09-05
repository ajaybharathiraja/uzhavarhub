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
        FarmerProfile.objects.get_or_create(user=farmer, defaults={'farm_name': 'Kaveri Delta Farms', 'location': 'Thanjavur, Tamil Nadu'})
        print("Created sample_farmer (password: farmer123)")
    else:
        # Just ensure profile exists
        FarmerProfile.objects.get_or_create(user=farmer, defaults={'farm_name': 'Kaveri Delta Farms', 'location': 'Thanjavur, Tamil Nadu'})

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
            'category': cat_objs['fresh-vegetables'], 'name': 'Ooty Carrots', 'slug': 'ooty-carrots',
            'description': 'Fresh, crunchy and naturally sweet carrots straight from the Nilgiris.',
            'price': 60.00, 'unit': 'kg', 'stock_quantity': 40
        },
        {
            'category': cat_objs['fresh-vegetables'], 'name': 'Pollachi Coconuts', 'slug': 'pollachi-coconuts',
            'description': 'Large, water-filled coconuts from the groves of Pollachi.',
            'price': 35.00, 'unit': 'piece', 'stock_quantity': 150
        },
        {
            'category': cat_objs['fresh-fruits'], 'name': 'Salem Mangoes (Imampasand)', 'slug': 'salem-mangoes',
            'description': 'The king of mangoes, rich and sweet, directly from Salem orchards.',
            'price': 150.00, 'unit': 'kg', 'stock_quantity': 30
        },
        {
            'category': cat_objs['dairy-eggs'], 'name': 'Country Chicken Eggs (Naattu Kozhi Muttai)', 'slug': 'naattu-kozhi-muttai',
            'description': 'Healthy country chicken eggs from free-ranging native breeds.',
            'price': 120.00, 'unit': 'dozen', 'stock_quantity': 25
        },
        {
            'category': cat_objs['grains-pulses'], 'name': 'Thanjavur Ponni Rice', 'slug': 'thanjavur-ponni-rice',
            'description': 'Premium quality, traditional boiled Ponni rice from the rice bowl of Tamil Nadu.',
            'price': 75.00, 'unit': 'kg', 'stock_quantity': 500
        },
        {
            'category': cat_objs['grains-pulses'], 'name': 'Erode Turmeric (Manjal)', 'slug': 'erode-turmeric',
            'description': 'High curcumin organic turmeric powder from Erode.',
            'price': 250.00, 'unit': 'kg', 'stock_quantity': 50
        }
    ]

    for p_data in products_data:
        Product.objects.get_or_create(
            slug=p_data['slug'],
            defaults={
                'farmer': farmer.farmer_profile,
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
