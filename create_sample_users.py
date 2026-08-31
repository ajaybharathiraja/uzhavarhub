import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uzhavarhub.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import CustomerProfile

User = get_user_model()

def create_samples():
    # Admin
    admin, created = User.objects.get_or_create(username='sample_admin', defaults={
        'email': 'admin@example.com',
        'role': 'ADMIN',
        'is_staff': True,
        'is_superuser': True
    })
    if created:
        admin.set_password('admin123')
        admin.save()
        print("Created sample_admin (password: admin123)")

    # Customer
    customer, created = User.objects.get_or_create(username='sample_customer', defaults={
        'email': 'customer@example.com',
        'role': 'CUSTOMER'
    })
    if created:
        customer.set_password('customer123')
        customer.save()
        CustomerProfile.objects.get_or_create(user=customer)
        print("Created sample_customer (password: customer123)")
        
    print("Sample users ensured.")

if __name__ == '__main__':
    create_samples()
