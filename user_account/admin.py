from django.contrib import admin
from . models import UserAccount, OTP

# Register your models here.
admin.site.register(UserAccount)
admin.site.register(OTP)