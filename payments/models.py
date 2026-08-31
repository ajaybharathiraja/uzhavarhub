from django.db import models
from django.conf import settings
from orders.models import Order

class Transaction(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='transaction')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)
    farmer_payout = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='PENDING') # PENDING, COMPLETED, REFUNDED
    gateway_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Calculate 5% platform commission if not set
        if not self.pk or (self.platform_fee == 0 and self.farmer_payout == 0):
            # Delivery fee is 40. Platform fee is 5% of (total - delivery).
            # But let's just make platform fee 5% of total for simplicity, or 5% of (total - 40).
            product_total = float(self.total_amount) - 40.0
            if product_total < 0:
                product_total = 0
            self.platform_fee = product_total * 0.05
            self.farmer_payout = product_total - self.platform_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"TXN-{self.id} for Order #{self.order.id}"
