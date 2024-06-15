from django.urls import path
from . import views

urlpatterns = [
    #Admin
    path('', views.users, name='users'),
    path('edit_user/<int:pk>/', views.edit_user, name='edit-user'),
    path('block_unblock_user/<int:pk>/', views.block_unblock_user, name='block_unblock_user'),
    
    #User
    path('my_orders/', views.my_orders, name='my-orders'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order-detail'),
    path('cancel_order/<int:order_number>/', views.cancel_order, name='cancel_order'),
    path('request_return/<int:order_number>/', views.request_return, name='request_return'),
    path('withdraw_return_request/<int:order_number>/', views.withdraw_return_request, name='withdraw_return_request'),

    path('continue_paypal_payments/', views.continue_paypal_payments, name='continue_paypal_payments'),
    path('continue_paypal_payments/order_complete/', views.continue_paypal_order_complete, name='continue_paypal_order_complete'),

    path('manage_address/', views.manage_address, name='manage-address'),
    path('add_new_address/', views.add_new_address, name='add-new-address'),
    path('edit-address/<int:address_id>/', views.edit_address, name='edit-address'),
    path('get-address-details/<int:address_id>/', views.get_address_details, name='get-address-details'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),

    path('profile_information/', views.profile_information, name='profile-information'),
    path('change_password/', views.change_password, name='change_password'),
    path('my_wallet/', views.my_wallet, name='my_wallet'),
    path('referral/', views.referral, name='referral'),
    path('apply_referral/', views.apply_referral, name='apply_referral'),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('add_wishlist/', views.add_wishlist, name='add_wishlist'),
    path('remove_wishlist/<int:product_id>/', views.remove_wishlist, name='remove_wishlist'),

]
