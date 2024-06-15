from django.contrib import admin
from . models import Product,ReviewRating,Variation
# Register your models here.
admin.site.register(Product)
admin.site.register(ReviewRating)
admin.site.register(Variation)