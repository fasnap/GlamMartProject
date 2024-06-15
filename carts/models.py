from django.db import models
from store.models import Product, Variation
from user_account.models import UserAccount
# Create your models here.

class Cart(models.Model):
    cart_id=models.CharField(max_length=100, blank=True)
    date_added=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    user=models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True)
    variations=models.ManyToManyField(Variation, blank=True)
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity=models.IntegerField()
    is_active=models.BooleanField(default=True)

    def product_total(self):
        return self.product.offer_price * self.quantity
    
    def __str__(self):
        return self.product.product_name
    

    

