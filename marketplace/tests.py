from django.test import TestCase
from accounts.models import User, FarmerProfile
from marketplace.models import Category, Product

class MarketplaceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='farmer1', password='pw', role='FARMER')
        self.farmer = FarmerProfile.objects.create(user=self.user, farm_name="My Farm", location="Location")
        self.category = Category.objects.create(name='Vegetables', slug='veg')
        self.product = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Tomato',
            slug='tomato',
            price=20.0,
            unit='kg',
            stock_quantity=100
        )
        
    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Tomato')
        self.assertEqual(self.product.category.name, 'Vegetables')
        self.assertEqual(self.product.farmer.user.username, 'farmer1')

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Vegetables')
        
    def test_product_str(self):
        self.assertEqual(str(self.product), 'Tomato')
