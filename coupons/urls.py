from django.urls import path
from . import views

urlpatterns = [
    path('checkCoupon/', views.checkCoupon, name="checkCoupon"),
    path('coupons/',views.coupons,name='coupons'),
    path('edit_coupon/<int:id>/',views.edit_coupon,name='edit_coupon'),
    path('delete_coupon/<int:id>/',views.delete_coupon,name='delete_coupon'),
    path('add_coupon/',views.add_coupon,name='add_coupon'),
]