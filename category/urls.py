from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.category, name='category'),
    path('add_category/', views.add_category, name='add-category'),
    path('<slug:category_slug>/activate_inactivate_category', views.activate_inactivate_category, name='activate_inactivate_category'),
    path('edit_category/<slug:category_slug>/', views.edit_category, name='edit-category'),

    path('sub_category/<slug:category_slug>/', views.sub_category, name='sub-category'),
    path('category/<slug:category_slug>/add_subcategory/', views.add_subcategory, name='add-subcategory'),
    path('category/<slug:subcategory_slug>/edit_subcategory/', views.edit_subcategory, name='edit-subcategory'),
    path('category/<slug:subcategory_slug>/activate_inactivate_subcategory/', views.activate_inactivate_subcategory, name='activate-inactivate-subcategory'),
   
]
