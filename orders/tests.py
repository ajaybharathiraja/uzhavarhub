from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, FarmerProfile, CustomerProfile
from marketplace.models import Category, Product
from orders.models import Order, OrderItem, Cart, CartItem

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
        self.assertTrue(self.order is not None)

class OrdersViewTests(TestCase):
    def setUp(self):
        self.client = Client()
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
        self.client.login(username='buyer1', password='pw')

    def test_add_to_cart_and_view(self):
        response = self.client.post(reverse('orders:add_to_cart', args=[self.product.id]), {'quantity': 2})
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('orders:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mango')

    def test_checkout(self):
        cart, _ = Cart.objects.get_or_create(user=self.user_buyer)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        response = self.client.post(reverse('orders:checkout'), {
            'shipping_address': '123 Test St'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.first().total_amount, 140.0)
        
    def test_order_history(self):
        Order.objects.create(customer=self.user_buyer, total_amount=100.0)
        response = self.client.get(reverse('orders:history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '100.0')
