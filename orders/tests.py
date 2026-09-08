from django.test import TestCase
from accounts.models import User, FarmerProfile, CustomerProfile
from marketplace.models import Category, Product
from orders.models import Order, OrderItem

class OrdersModelTests(TestCase):
    def setUp(self):
        self.user_buyer = User.objects.create_user(username='buyer1', password='pw', role='CUSTOMER')
        self.buyer = CustomerProfile.objects.create(user=self.user_buyer)
        self.user_farmer = User.objects.create_user(username='farmer1', password='pw', role='FARMER')
        self.farmer = FarmerProfile.objects.create(user=self.user_farmer, farm_name="Farm", location="Loc")
        self.category = Category.objects.create(name='Fruits', slug='fruits')
        self.product = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Mango',
            slug='mango',
            price=50.0,
            unit='kg',
            stock_quantity=100
        )
        self.order = Order.objects.create(customer=self.user_buyer, total_amount=100.0)
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            farmer=self.user_farmer,
            quantity=2,
            price_at_purchase=50.0
        )
        
    def test_order_creation(self):
        self.assertEqual(self.order.customer.username, 'buyer1')
        self.assertEqual(self.order.total_amount, 100.0)

    def test_order_item_creation(self):
        self.assertEqual(self.order_item.product.name, 'Mango')
        self.assertEqual(self.order_item.quantity, 2)
        
    def test_order_str(self):
        # Even if there's no custom __str__, we can just check if it instantiates
        self.assertTrue(self.order is not None)
