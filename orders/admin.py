from django.contrib import admin
from . models import Payment,Order,OrderProduct, ReturnRequest
# Register your models here.


class OrderProductInline(admin.TabularInline):
    model=OrderProduct
    extra=0

class OrderAdmin(admin.ModelAdmin):
    inlines=[OrderProductInline]

admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(ReturnRequest)
