from django.contrib import admin
from .models import Coupons
from .models import CouponCheck


admin.site.register(Coupons)
admin.site.register(CouponCheck)