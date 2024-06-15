from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.user_home, name='user-home'),
    path('user_login/', views.user_login, name='user-login'),
    path('user_register', views.user_register, name='user-register'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('verify_otp/<int:otp_id>/', views.verify_otp, name='verify_otp'),
    path('resend_otp/<int:otp_id>/', views.resend_otp, name='resend_otp'),
    path('forgot_password/', views.forgot_password, name='forgot-password'),
    path('verify-otp/<int:otp_id>/', views.verify_forgot_password_otp, name='verify_forgot_password_otp'),
    path('resend_forgot_otp/<int:otp_id>/', views.resend_forgot_otp, name='resend_forgot_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
]
