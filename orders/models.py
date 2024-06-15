from django.db import models
from user_account.models import UserAccount
from users.models import UserAddress
from store.models import Product,Variation
from coupons.models import Coupons,CouponCheck
# Create your models here.

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES=(
        ('PayPal','PayPal'),
        ('cod','cod'),
    )
    user=models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    payment_id=models.CharField(max_length=100)
    payment_method=models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES)
    amount_paid=models.CharField(max_length=100)
    status=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.payment_id
    
class Order(models.Model):
    STATUS=(
        ('New','New'),
        ('Ordered','Ordered'),
        ('Shipped','Shipped'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled'),
        ('Returned','Returned')
    )
    user=models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True)
    payment=models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number=models.CharField(max_length=20)
    address=models.ForeignKey(UserAddress, on_delete=models.SET_NULL, null=True)
    order_note=models.CharField(max_length=100, blank=True)
    order_total=models.IntegerField()
    delivery_charge=models.IntegerField()
    status=models.CharField(max_length=10,choices=STATUS, default='New')
    ip=models.CharField(blank=True, max_length=20)
    is_ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey(Coupons, on_delete=models.SET_NULL, blank=True, null=True)
    discount = models.FloatField(null=True)
    
    def __str__(self):
        return self.order_number

class OrderProduct(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL, blank=True, null=True)
    user=models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    variations=models.ManyToManyField(Variation, blank=True)
    quantity=models.IntegerField()
    product_price=models.IntegerField()
    ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name
    
class ReturnRequest(models.Model):
    REJECT_REQUEST_STATUS=(
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Rejected','Rejected'),
    )
    order=models.ForeignKey(Order, on_delete=models.CASCADE)
    reason=models.TextField()
    status=models.CharField(choices=REJECT_REQUEST_STATUS, default='Pending', max_length=20)
    


