import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uzhavarhub.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import FarmerProfile

User = get_user_model()

def seed_farmers():
    farmers_data = [
        {
            'username': 'vaigai_farmer',
            'email': 'vaigai@example.com',
            'farm_name': 'Vaigai Organics',
            'location': 'Madurai, Tamil Nadu',
            'is_verified': True
        },
        {
            'username': 'kongu_farmer',
            'email': 'kongu@example.com',
            'farm_name': 'Kongu Naturals',
            'location': 'Coimbatore, Tamil Nadu',
            'is_verified': True
        },
        {
            'username': 'nilgiri_farmer',
            'email': 'nilgiri@example.com',
            'farm_name': 'Nilgiri Fresh',
            'location': 'Ooty, Tamil Nadu',
            'is_verified': False
        },
        {
            'username': 'kumari_farmer',
            'email': 'kumari@example.com',
            'farm_name': 'Kumari Coast Farms',
            'location': 'Kanyakumari, Tamil Nadu',
            'is_verified': True
        }
    ]

    for data in farmers_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'role': 'FARMER'
            }
        )
        
        if created:
            user.set_password('farmer123')
            user.save()
            print(f"Created user: {data['username']}")

        profile, profile_created = FarmerProfile.objects.get_or_create(
            user=user,
            defaults={
                'farm_name': data['farm_name'],
                'location': data['location'],
                'is_verified': data['is_verified']
            }
        )
        if not profile_created:
            profile.farm_name = data['farm_name']
            profile.location = data['location']
            profile.is_verified = data['is_verified']
            profile.save()
            
        print(f"Ensured profile for: {data['farm_name']}")

if __name__ == '__main__':
    seed_farmers()
    print("Successfully seeded more farmers!")
