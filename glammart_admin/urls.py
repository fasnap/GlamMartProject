from django.urls import path
from . import views

urlpatterns = [
    path('',views.admin_home, name='admin-home'),
    path('admin_login/', views.admin_login, name='admin-login'),
    path('admin_logout/', views.admin_logout, name='admin-logout')
]
