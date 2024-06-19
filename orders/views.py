import json
import time
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render,redirect, get_object_or_404
from carts.models import CartItem
from users.models import UserAddress, Wallet, WalletTransaction
from . models import Order,Payment,OrderProduct, ReturnRequest
from store.models import Product
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from coupons.models import CouponCheck,Coupons
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter,landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import xlsxwriter
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# Create your views here.
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required(login_url='user-login')
def paypal_payments(request):
    print("hi----------------------hi")
    csrf_token = request.META.get("CSRF_COOKIE")
    print(csrf_token)
  
    body=json.loads(request.body)
    try:
        order=Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
        # Store transaction details inside payment model
        payment=Payment(
            user = request.user,
            payment_id = body['transID'],
            payment_method = body['payment_method'],
            amount_paid = order.order_total,
            status=body['status']
        )
        payment.save()
        order.payment=payment
        order.is_ordered=True
        order.save()
        if 'coupon_id' in request.session:
            coupon_id=request.session['coupon_id']
            coupon=Coupons.objects.get(id=coupon_id)
            CouponCheck.objects.create(user=request.user, coupon=coupon)
            
            del request.session['coupon_id']
            del request.session['sub_total']
            del request.session['discount_price']
        # Move the cart item to Order product table
        cart_items=CartItem.objects.filter(user=request.user, is_active=True)
        for item in cart_items:
            orderproduct=OrderProduct()
            orderproduct.order_id=order.id
            orderproduct.payment=payment
            orderproduct.user_id=request.user.id
            orderproduct.product_id=item.product_id
            orderproduct.quantity=item.quantity
            orderproduct.product_price=item.product.offer_price
            orderproduct.ordered=True
            orderproduct.save()

            # Assigning variations into orderproduct table(variations can be assign only after saving the orderproduct instance, because variations is many to many field)
            cart_item=CartItem.objects.get(id=item.id)
            product_variation=cart_item.variations.all()
            orderproduct=OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            # Reduce quantity of sold products
            product=Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            if product.stock <=0 :
                product.is_available=False
            product.save()

        # Clear cart after successfull order
        CartItem.objects.filter(user=request.user).delete()
        
        # Send order success mail to user
        send_mail(
            'Thank YOu For Your Order',
            'We have received your order, Enjoy sopping with GlamMart',
            'testmaildjango27121995@gmail.com',
            [request.user.email],
            fail_silently=False,
        )
        order.status='Ordered'
        order.save()
        # Send order number and transaction id back to sendData method via json response
        data={
            'order_number': order.order_number,
            'transID': payment.payment_id,
        }
        return JsonResponse(data)
    except Exception as e:
        print("Error: ", e)
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='user-login')
def paypal_order_complete(request):
    order_number=request.GET.get('order_number')
    transID=request.GET.get('payment_id')
    try:
        order=Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products=OrderProduct.objects.filter(order_id=order.id)
        subtotal=0
        for i in ordered_products:
            subtotal=i.product_price * i.quantity

        payment=Payment.objects.get(payment_id=transID)
        context={
            'order':order,
            'ordered_products':ordered_products,
            'order_number':order.order_number,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal
        }    
        return render(request,'glam_user/paypal_order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('user-home')


# for cod
@login_required(login_url='user-login')
def payments(request):
    if request.method=='POST':
        payment_method=request.POST.get('payment_method')
        order_number = request.session.get('order_number')
        if payment_method == 'cod' and order_number:
            
            try:
                order=Order.objects.get(user=request.user, is_ordered=False, order_number=order_number )
                payment_id='cod'+order_number
                if order:
                    payment=Payment(
                    user=request.user,
                    payment_id=payment_id,
                    payment_method='cod',
                    amount_paid=order.order_total,
                    status='Pending',
                    )
                payment.save()
                order.payment=payment
                order.is_ordered=True
                order.save()
                if 'coupon_id' in request.session:
                    coupon_id=request.session['coupon_id']
                    coupon=Coupons.objects.get(id=coupon_id)
                    CouponCheck.objects.create(user=request.user, coupon=coupon)
                    order.discount = request.session.get('discount_price', 0)

                    del request.session['coupon_id']
                    del request.session['sub_total']
                    del request.session['discount_price']
                order.save()
                # Moving cart items to OrderProduct table
                cart_items=CartItem.objects.filter(user=request.user, is_active=True)
                for item in cart_items:
                    orderproduct=OrderProduct()
                    orderproduct.order_id=order.id
                    orderproduct.payment=payment
                    orderproduct.user_id=request.user.id
                    orderproduct.product_id=item.product_id
                    orderproduct.quantity=item.quantity
                    orderproduct.product_price=item.product.offer_price
                    orderproduct.ordered=True
                    orderproduct.save()
                    
                    # Assigning variations into orderproduct table(variations can be assign only after saving the orderproduct instance, because variations is many to many field)
                    cart_item=CartItem.objects.get(id=item.id)
                    product_variation=cart_item.variations.all()
                    orderproduct=OrderProduct.objects.get(id=orderproduct.id)
                    orderproduct.variations.set(product_variation)
                    orderproduct.save()

                    # Reduce quantity of sold products
                    product=Product.objects.get(id=item.product_id)
                    product.stock -= item.quantity
                    if product.stock <=0 :
                        product.is_available=False
                    product.save()
                
                # Clear cart after successfull order
                CartItem.objects.filter(user=request.user).delete()

                # Send mail to user about order received 
                send_mail(
                    'Thank YOu For Your Order',
                    'We have received your order, Enjoy sopping with GlamMart',
                    'testmaildjango27121995@gmail.com',
                    [request.user.email],
                    fail_silently=False,
                )
                order.status='Ordered'
                order.save()
                context={
                    'order':order,
                    'order_number':order_number,
                }
                return render(request,'glam_user/cod_complete.html',context)
            
            except Order.DoesNotExist:
                pass
        else:
            # Invalid payment method selected

            return render(request, 'glam_user/payments.html', {'error_message': 'Invalid payment method selected'})
       
    else:
        return render(request,'glam_user/payments.html')

@login_required(login_url='user-login')
def place_order(request,total=0,quantity=0):
    current_user=request.user
    cart_items=CartItem.objects.filter(user=current_user, is_active=True)
  
    cart_count=cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total=0
    delivery_charge=0

    for cart_item in cart_items:
        if not cart_item.product.is_available or cart_item.product.stock <= 0:
                cart_item.is_active = False
                cart_item.save()
        else:
            total += (cart_item.product.offer_price * cart_item.quantity)
            quantity += cart_item.quantity
   
    cart_items = CartItem.objects.filter(user=current_user, is_active=True)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('store')
    
    if total<500 and total!=0:
        delivery_charge=50
        
    grand_total=total+delivery_charge

    if 'coupon_id' in request.session:
        discount = request.session['discount_price']
        grand_total = request.session['sub_total']
    else:
        discount = 0

    if request.method=='POST':
        selected_address_id = request.POST.get('address_id')
        order_note=request.POST.get('order_note')
        ip=request.META.get('REMOTE_ADDR')

        if selected_address_id:
            try:
                selected_address=UserAddress.objects.get(id=selected_address_id)
                
                order=Order(
                    user=request.user,
                    address=selected_address,
                    order_note=order_note, 
                    order_total=grand_total,
                    delivery_charge=delivery_charge,
                    ip=ip,
                    discount=discount,
                    )
                order.save()
                timestamp = int(time.time() * 1000)  # Current timestamp in milliseconds
                order_number = f'{timestamp}{order.id}'
                order.order_number = order_number
                order.save()
                request.session['order_number'] = order_number
                orders=Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
                context={
                    'orders':orders,
                    'cart_items':cart_items,
                    'total':total,
                    'delivery_charge':delivery_charge,
                    'grand_total':grand_total,
                    'order_number':order_number,
                    'discount':discount,
                }
                return render(request,'glam_user/payments.html',context)
                
            except UserAddress.DoesNotExist:
                return render(request,'glam_user/checkout.html')
        else:
            first_name=request.POST['first_name']
            last_name=request.POST['last_name']
            phone_number=request.POST['phone_number']
            email=request.POST['email']
            address_line1=request.POST['address_line1']
            address_line2=request.POST['address_line2']
            country=request.POST['country']
            state=request.POST['state']
            city=request.POST['city']
            zip_code=request.POST['zip_code']
            order_note=request.POST.get('order_note')
            
            if UserAddress.objects.filter(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                email=email,
                address_line1=address_line1,
                address_line2=address_line2,
                country=country,
                state=state,
                city=city,
                zip_code=zip_code
            ).exists():
                new_address = UserAddress.objects.filter(
                    user=request.user,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    email=email,
                    address_line1=address_line1,
                    address_line2=address_line2,
                    country=country,
                    state=state,
                    city=city,
                    zip_code=zip_code
                ).first()
            else:
                new_address=UserAddress(
                    user=request.user,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    email=email,
                    address_line1=address_line1,
                    address_line2=address_line2,
                    country=country,
                    state=state,
                    city=city,
                    zip_code=zip_code,
                )
                new_address.save()

            order=Order(
                user=request.user,
                address=new_address,
                order_note=order_note,
                order_total=grand_total,
                delivery_charge=delivery_charge,
                ip=ip,  
                discount=discount,
                )
            order.save()
            timestamp = int(time.time() * 1000)  # Current timestamp in milliseconds
            order_number = f'{timestamp}{order.id}'
            order.order_number = order_number
            order.save()
            request.session['order_number'] = order_number
            orders=Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context={
                'orders':orders,
                'cart_items':cart_items,
                'total':total,
                'delivery_charge':delivery_charge,
                'grand_total':grand_total,
                'order_number':order_number,
                'discount':discount,
            }
            return render(request,'glam_user/payments.html',context)
    else:
       return redirect('checkout')

# Admin side view all orders    
@login_required(login_url='admin-login')   
def orders(request):
    query=request.GET.get('q')
    if query:
        orders=Order.objects.filter(
            Q(order_number__icontains=query) | 
            Q(user__username__icontains=query) | 
            Q(status__icontains=query) | 
            Q(payment__payment_method__icontains=query),
            is_ordered=True,
        ).exclude(status='New').order_by('-created_at')
    else:
        orders=Order.objects.filter(is_ordered=True).exclude(status='New').order_by('-created_at')
    
    paginator=Paginator(orders, 10)
    page=request.GET.get('page')
    try:
        paged_orders=paginator.get_page(page)
    except PageNotAnInteger:
        paged_orders = paginator.page(1)
    except EmptyPage:
        paged_orders = paginator.page(paginator.num_pages)
    context={
        'orders':paged_orders,
        'query': query,
    }
    return render(request,'glam_admin/orders.html', context)

# Admin side order detail page
@login_required(login_url='admin-login') 
def orders_detail(request,order_id):
    order_detail=OrderProduct.objects.filter(order__order_number=order_id)
    order=Order.objects.get(order_number=order_id)
    
    context={
        'order_detail':order_detail,
        'order':order,
        'discount': order.discount if order.discount else 0
    }
    return render(request,'glam_admin/orders_detail.html', context)

# Admin side update order status
@login_required(login_url='admin-login') 
@csrf_exempt
def update_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            new_status = data.get('status')

            order = Order.objects.get(id=order_id)
            order.status = new_status
            if new_status == 'Delivered' and order.payment.status=='Pending':
                order.payment.status='COMPLETED'
            order.save()
            order.payment.save() 

            return JsonResponse({'success': True, 'new_status': order.get_status_display()})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Admin return request list
@login_required(login_url='admin-login') 
def return_requests(request):
    query=request.GET.get('q')
    if query:
        return_requests = ReturnRequest.objects.filter(
            Q(order__order_number__icontains=query) |
            Q(order__user__username__icontains=query) |
            Q(reason__icontains=query) |
            Q(status__icontains=query)
        )
    else:
        return_requests = ReturnRequest.objects.all()

    paginator=Paginator(return_requests, 10)
    page=request.GET.get('page')
    try:
        paged_return_requests=paginator.get_page(page)
    except PageNotAnInteger:
        paged_return_requests = paginator.page(1)
    except EmptyPage:
        paged_return_requests = paginator.page(paginator.num_pages)

    context={
        'return_requests': paged_return_requests,
        'query':query
    }
    return render(request, 'glam_admin/return_requests.html', context)

# Admin updated return request status
@login_required(login_url='admin-login') 
def update_return_request_status(request, request_id, status):
    return_request=get_object_or_404(ReturnRequest, id=request_id)
    if status in dict(ReturnRequest.REJECT_REQUEST_STATUS).keys():
        return_request.status=status
        return_request.save()
        if return_request.status=='Approved' and return_request.order.payment.status=='COMPLETED':
            user_wallet=Wallet.objects.get(user=return_request.order.user)
            refunded_amount=return_request.order.order_total - return_request.order.delivery_charge
            user_wallet.balance += refunded_amount
            user_wallet.save()
            WalletTransaction.objects.create(wallet=user_wallet, amount=refunded_amount, description=f"Refund for returned order #{return_request.order.order_number}")
            return_request.save()
            return_request.order.payment.status='REFUNDED'
            return_request.order.payment.save()
            return_request.order.status='Returned'
            return_request.order.save()
        messages.success(request,f'Return request {status.lower()} updated successfully.')
    else:
        messages.error(request,'Invalid status')
    return redirect('return_requests')

# Admin side sales report page

def sales_report(request):
    date_range = request.GET.get('date_range', 'till_now')
    today = timezone.now().date()
    total_success_order_amount = 0
    total_discount_amount=0
    orders = Order.objects.all().order_by('-created_at').exclude(status='New')
    start_date = None
    end_date = None
    if date_range == 'today':
        orders = orders.filter(created_at__date=today)
    elif date_range == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
        orders = orders.filter(created_at__date__range=[start_date, end_date])
    elif date_range == 'monthly':
        start_date = today.replace(day=1)
        end_date = today
        orders = orders.filter(created_at__date__range=[start_date, end_date])
    elif date_range == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today
        orders = orders.filter(created_at__date__range=[start_date, end_date])
    elif date_range == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and not end_date:
            orders = orders.filter(created_at__date__gte=start_date)
        elif end_date and not start_date:
            orders = orders.filter(created_at__date__lte=end_date)
        else:
            orders = orders.filter(created_at__date__range=[start_date, end_date])
    else:
        orders = orders.all()

    total_success_orders = orders.filter(payment__status='COMPLETED')

    for order in orders:
        if order.discount:
            total_discount_amount += order.discount if order.discount is not None else 0.0
        
    for order in total_success_orders:
        total_success_order_amount += order.order_total

    total_orders_count = orders.count()

    context = {
        'orders': orders,
        'total_orders_count': total_orders_count,
        'total_success_order_amount': total_success_order_amount,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'total_discount_amount':total_discount_amount,
    }
    return render(request, 'glam_admin/sales_report.html', context)

# Admin side pdf generatin of sales report

def generate_pdf(orders, total_orders_count, total_success_order_amount,total_discount_amount):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []

    order_data = [['Order Number', 'User', 'Date', 'Paid Amount', 'Delivery Charge', 'payment Status', 'Payment Method', 'Discount', 'Order Status']]
    for order in orders:
        order_data.append([
            str(order.order_number),
            order.user.username,
            order.created_at.strftime("%d-%m-%Y"),
            str(order.order_total),
            str(order.delivery_charge),
            order.payment.status if order.payment else '',
            order.payment.payment_method if order.payment else '',
            str(order.discount),
            order.status if order.status else '',
        ])
    num_columns = len(order_data[0])
    page_width = landscape(letter)[0] - 2 * 36
    column_width = page_width / num_columns

    table = Table(order_data, colWidths=[column_width] * num_columns)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    # Add Paragraph wrapping for text cells
    styles = getSampleStyleSheet()
    for i, row in enumerate(order_data):
        for j, cell in enumerate(row):
            if isinstance(cell, str):
                order_data[i][j] = Paragraph(cell, styles['BodyText'])
    elements.append(table)
    # Adding totals
    elements.append(Paragraph("Overall Sales Count: " + str(total_orders_count), styles['Normal']))
    elements.append(Paragraph("Overall Success Order Amount: " + str(total_success_order_amount), styles['Normal']))
    elements.append(Paragraph("Overall Discount: " + str(total_discount_amount), styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# Admin side downloading generated pdf

def download_sales_report_pdf(request):
    date_range = request.GET.get('date_range', 'till_now')
    today = timezone.now().date()
    total_success_order_amount = 0
    total_discount_amount=0
    orders = Order.objects.all().order_by('-created_at')
    start_date = None
    end_date = None
    if date_range == 'today':
        orders = orders.filter(created_at__date=today)
    elif date_range == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
        orders = orders.filter(created_at__date__range=[start_date, end_date])
    elif date_range == 'monthly':
        start_date = today.replace(day=1)
        end_date = today
        orders = orders.filter(created_at__date__range=[start_date, end_date])
    elif date_range == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today
        orders = orders.filter(created_at__date__range=[start_date, end_date])
    elif date_range == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and not end_date:
            orders = orders.filter(created_at__date__gte=start_date)
        elif end_date and not start_date:
            orders = orders.filter(created_at__date__lte=end_date)
        else:
            orders = orders.filter(created_at__date__range=[start_date, end_date])
    else:
        orders = orders.all()
    
    total_success_orders = orders.filter(payment__status='COMPLETED')
    for order in total_success_orders:
        total_success_order_amount += order.order_total
    
    for order in orders:
        if order.discount:
            total_discount_amount += order.discount if order.discount is not None else 0.0
        
    total_orders_count = orders.count()

    buffer = generate_pdf(orders, total_orders_count, total_success_order_amount, total_discount_amount)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    return response

# Admin side sales report excel file generating
def generate_excel(orders, total_orders_count, total_success_order_amount, total_discount_amount):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Add headers to the worksheet
    headers = ['Order Number', 'User', 'Date', 'Paid Amount', 'Delivery Charge', 'Discount', 'Payment Status', 'Payment Method', 'Order Status']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    # Initialize row variable
    row = 1

    # Write data rows to the worksheet
    for order in orders:
        worksheet.write(row, 0, order.order_number)
        worksheet.write(row, 1, order.user.username)
        worksheet.write(row, 2, order.created_at.strftime("%d-%m-%Y"))
        worksheet.write(row, 3, str(order.order_total))
        worksheet.write(row, 4, str(order.delivery_charge))
        worksheet.write(row, 5, str(order.discount))
        worksheet.write(row, 6, order.payment.status if order.payment else '')
        worksheet.write(row, 7, order.payment.payment_method if order.payment else '')
        worksheet.write(row, 8, order.status if order.status else '')
        row += 1

    # Add total orders and total success order amount to the worksheet
    worksheet.write(row + 1, 0, 'Overall Sales Count:')
    worksheet.write(row + 1, 1, total_orders_count)
    worksheet.write(row + 2, 0, 'Overall Success Order Amount:')
    worksheet.write(row + 2, 1, total_success_order_amount)
    worksheet.write(row + 3, 0, 'Overall Discount:')
    worksheet.write(row + 3, 1, total_discount_amount)

    workbook.close()
    output.seek(0)
    return output

# Admin side downloading generated excel file

def download_sales_report_excel(request):
    date_range = request.GET.get('date_range', 'till_now')
    today = timezone.now().date()
    total_success_order_amount = 0
    total_discount_amount=0
    orders = Order.objects.all().order_by('-created_at')
    start_date = None
    end_date = None
    if date_range == 'today':
        orders = orders.filter(created_at__date=today)
    elif date_range == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
        orders = orders.filter(created_at__date__range=([start_date, end_date]))
    elif date_range == 'monthly':
        start_date = today.replace(day=1)
        end_date = today
        orders = orders.filter(created_at__date__range=([start_date, end_date]))
    elif date_range == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today
        orders = orders.filter(created_at__date__range=([start_date, end_date]))
    elif date_range == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and not end_date:
            orders = orders.filter(created_at__date__gte=start_date)
        elif end_date and not start_date:
            orders = orders.filter(created_at__date__lte=end_date)
        else:
            orders = orders.filter(created_at__date__range=([start_date, end_date]))
    else:
        orders = orders.all()
    
    total_success_orders = orders.filter(payment__status='COMPLETED')
    for order in total_success_orders:
        total_success_order_amount += order.order_total
    
    for order in orders:
        if order.discount:
            total_discount_amount += order.discount if order.discount is not None else 0.0
        
    total_orders_count = orders.count()

    excel_output = generate_excel(orders, total_orders_count, total_success_order_amount, total_discount_amount)
    response = HttpResponse(excel_output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
    return response