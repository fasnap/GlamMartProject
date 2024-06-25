from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add-cart'),
    path('remove_cart_item/<int:product_id>//<int:cart_item_id>/', views.remove_cart_item, name='remove-cart-item'),
    path('checkout/', views.checkout, name='checkout'),
    path('increment_cart_item/', views.increment_cart_item, name='increment-cart-item'),
    path('decrement_cart_item/', views.decrement_cart_item, name='decrement-cart-item'),
    path('get_cart_totals/', views.get_cart_totals, name='get-cart-totals'),
     
]
