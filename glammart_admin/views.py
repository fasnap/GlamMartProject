from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from store.models import Product
from category.models import SubCategory
from django.db.models import Count, Sum, F
from user_account.models import UserAccount
from orders.models import Order, OrderProduct
from category.models import Category
from django.db.models.functions import TruncMonth, TruncYear, TruncDay
from django.utils.text import Truncator
from django.utils import timezone

# Create your views here.
def truncate_name(name,length):
    return Truncator(name).chars(length, truncate='...')

@never_cache
def admin_home(request):
    if request.user.is_authenticated and request.user.is_superuser:
        best_selling_products=Product.objects.all().annotate(num_orders=Count('orderproduct')).order_by('-num_orders')[:10]
        best_selling_subcategory=SubCategory.objects.all().annotate(num_orders=Count('product__orderproduct')).order_by('-num_orders')[:6]
        active_users=UserAccount.objects.filter(is_active=True).count()
        total_orders=Order.objects.all().exclude(status='New').count()
        total_products=Product.objects.all().count()
        total_sales=0
        
        orders=Order.objects.filter(payment__status='COMPLETED')
        orders_delivered=Order.objects.filter(status='Delivered').count()
        orders_shipped=Order.objects.filter(status='Shipped').count()
        orders_cancelled=Order.objects.filter(status='Cancelled').count()
        orders_returned=Order.objects.filter(status='Returned').count()
        for order in orders:
            total_sales += order.order_total

        # Most selling products chart
        most_selling_products=OrderProduct.objects.values('product__product_name').annotate(product_count=Sum('quantity')).order_by('-product_count')
        product_labels = []
        product_data = []
        for item in most_selling_products:
            product_labels.append(truncate_name(item['product__product_name'], 10))
            product_data.append(item['product_count'])
        
        # Most selling sub categories chart
        most_selling_subcategories=OrderProduct.objects.values('product__sub_category__sub_category_name').annotate(subcategory_count=Sum('quantity')).order_by('-subcategory_count')
        subcategory_labels = []
        subcategory_data = []
        for item in most_selling_subcategories:
            subcategory_labels.append(item['product__sub_category__sub_category_name'])
            subcategory_data.append(item['subcategory_count'])

        today = timezone.now()
        filter_type = request.GET.get('filter', 'daily')

        if filter_type == 'daily':
            sales = Order.objects.filter(payment__status='COMPLETED').annotate(day=TruncDay('created_at')).values('day').annotate(total_sales=Sum('order_total')).order_by('day')
            labels = [sale['day'].strftime('%d %B %Y') for sale in sales]
            data = [sale['total_sales'] for sale in sales]
        elif filter_type == 'monthly':
            sales = Order.objects.filter(payment__status='COMPLETED').annotate(month=TruncMonth('created_at')).values('month').annotate(total_sales=Sum('order_total')).order_by('month')
            labels = [sale['month'].strftime('%B %Y') for sale in sales]
            data = [sale['total_sales'] for sale in sales]
        elif filter_type == 'yearly':
            sales = Order.objects.filter(payment__status='COMPLETED').annotate(year=TruncYear('created_at')).values('year').annotate(total_sales=Sum('order_total')).order_by('year')
            labels = [sale['year'].strftime('%Y') for sale in sales]
            data = [sale['total_sales'] for sale in sales]

        context={
            'best_selling_products':best_selling_products,
            'best_selling_subcategory':best_selling_subcategory,
            'active_users':active_users,
            'total_orders':total_orders,
            'total_products':total_products,
            'total_sales':total_sales,
            'orders_delivered':orders_delivered,
            'orders_shipped':orders_shipped,
            'orders_cancelled':orders_cancelled,
            'orders_returned':orders_returned,
            'product_labels': product_labels,
            'product_data': product_data,
            'subcategory_labels':subcategory_labels,
            'subcategory_data':subcategory_data,
            'labels':labels,
            'data':data,
        }
        return render(request,'glam_admin/admin_home.html', context)
    else:
        return redirect('admin-login')

@never_cache
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin-home')
        
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user = authenticate(email=email,password=password)
        if user is not None and user.is_superuser:
            login(request,user)
            return redirect('admin-home')
        elif not email or not password:
            messages.error(request,'Please enter email and password')
            return redirect('admin-login')
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('admin-login')
    return render(request,'glam_admin/login.html')

@login_required(login_url='admin-login')
def admin_logout(request):
    logout(request)
    return redirect('admin-login')
