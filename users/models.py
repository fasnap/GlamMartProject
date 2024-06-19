from django.db import models
from user_account.models import UserAccount
from django.utils import timezone
from store.models import Product
# Create your models here.
class UserProfile(models.Model):
    GENDER_CHOICES=[
        ('M','Male'),
        ('F','Female'),
        ('O','Other'),
    ]
    user=models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    profile_picture=models.ImageField(upload_to='photos/profile_pictures', blank=True, null=True)
    date_of_birth=models.DateField(blank=True, null=True)
    gender=models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    referral_code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    referred_by=models.ForeignKey(UserAccount, on_delete=models.SET_NULL, related_name='referrals', null=True, blank=True)
    
    def __str__(self):
        return self.user.first_name
    
class UserAddress(models.Model):
    user=models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100,blank=True, null=True)
    email=models.EmailField(max_length=100)
    phone_number=models.CharField(max_length=100)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True, null=True)
    country=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    zip_code=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_deleted=models.BooleanField(default=False)
    is_default=models.BooleanField(default=False)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        return f'{self.address_line1} {self.address_line2}'
    def __str__(self):
        return self.first_name

class Wallet(models.Model):
    user=models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    balance=models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class WalletTransaction(models.Model):
    wallet=models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    description=models.CharField(max_length=250)
    timestamp=models.DateTimeField(auto_now_add=True)
    
class WishList(models.Model):
    user=models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)