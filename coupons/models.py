from django.db import models
from user_account.models import UserAccount

# Create your models here.
class Coupons(models.Model):
    coupon_name=models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    discount = models.CharField(max_length=3)
    status = models.BooleanField(default=True)
    date = models.DateField(auto_now_add=True)
    valid_to=models.DateField()
    valid_from=models.DateField()

    def __str__(self):
        return self.code
    
class CouponCheck(models.Model):
    coupon = models.ForeignKey(Coupons, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)