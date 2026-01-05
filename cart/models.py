from django.db import models


# Create your models here.

""" 
from models_app.models import ShoeVariant
from customer.models import Customer

class CartItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cart_items')
    variant = models.ForeignKey(ShoeVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.variant.shoe.price * self.quantity

    def __str__(self):
        return f"{self.variant} (x{self.quantity})"
 """