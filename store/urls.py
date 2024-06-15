from django.urls import path
from . import views

urlpatterns = [
    # Admin side 
    path('', views.product, name='product'),
    path('add_product/', views.add_product, name='add-product'),
    path('<slug:product_slug>/activate_inactivate_product', views.activate_inactivate_product, name='activate_inactivate_product'),
    path('<slug:product_slug>/edit_product', views.edit_product, name='edit_product'),
    path('variation/', views.variations, name='variations'),
    path('variation/add_variation/', views.add_variation, name='add-variation'),
    path('variation/edit_variation/<int:variation_id>/', views.edit_variation, name='edit_variation'),
    path('activate_inactivate_variation/<int:variation_id>/', views.activate_inactivate_variation, name='activate_inactivate_variation'),
    
    #User side
    path('store/', views.store, name='store'),
    path('store/<slug:category_slug>/', views.store, name='product-by-category'),
    path('store/<slug:category_slug>/<slug:sub_category_slug>/', views.store, name='product-by-sub-category'),
    path('store/product_detail/<slug:category_slug>/<slug:sub_category_slug>/<slug:product_slug>/', views.product_detail, name='product-detail'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),

    path('get-subcategories/', views.get_subcategories, name='get-subcategories'),
]
