from django.urls import path
from . import views

urlpatterns = [
    # User side
    path('place_order/', views.place_order, name='place-order'),
    path('payments/', views.payments, name='payments'),
    path('paypal_payments/', views.paypal_payments, name='paypal_payments'),
    path('paypal_payments/order_complete/', views.paypal_order_complete, name='paypal_order_complete'),

    # Admin Side
    path('orders/', views.orders, name='orders'),
    path('orders_detail/<int:order_id>/', views.orders_detail, name='orders-detail'),
    path('update_status/', views.update_status, name='update_status'),
    path('return_requests/', views.return_requests, name='return_requests'),
    path('update_return_request_status/<int:request_id>/<str:status>/',views.update_return_request_status, name='update_return_request_status'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    
    path('download-sales-report-pdf/', views.download_sales_report_pdf, name='download_sales_report_pdf'),
    path('download_sales_report_excel/', views.download_sales_report_excel, name='download_sales_report_excel'),
]
