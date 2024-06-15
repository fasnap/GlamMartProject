from django.contrib import admin
from . models import UserAccount,UserAddress,UserProfile,Wallet,WishList
# Register your models here.

admin.site.register(UserAddress)
admin.site.register(UserProfile)
admin.site.register(Wallet)
admin.site.register(WishList)