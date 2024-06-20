import json
from django.shortcuts import get_object_or_404, render,redirect
from user_account.models import UserAccount
from . models import UserAddress,UserProfile, Wallet, WishList, WalletTransaction
from orders.models import Order,OrderProduct, ReturnRequest, Payment
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages
from . forms import UserForm,UserProfileForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict

# Admin view all users
@login_required(login_url='admin-login')
def users(request):
    query=request.GET.get('q')
    if query:
        registered_users = UserAccount.objects.filter(
            Q(username__icontains=query)|
            Q(first_name__icontains=query)|
            Q(last_name__icontains=query)
        )
    else:
        registered_users = UserAccount.objects.all()
    
    paginator=Paginator(registered_users, 10)
    page=request.GET.get('page')
    try:
        paged_registered_users=paginator.get_page(page)
    except PageNotAnInteger:
        paged_registered_users = paginator.page(1)
    except EmptyPage:
        paged_registered_users = paginator.page(paginator.num_pages)
    context={
        'registered_users' : paged_registered_users,
        'query':query,
    }
    return render(request, 'glam_admin/users.html', context)

# Admin editl user
@login_required(login_url='admin-login')
def edit_user(request,pk):
    user=UserAccount.objects.get(pk=pk)
    if request.method=='POST':
        username=request.POST['username']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        phone_number=request.POST['phone_number']
        user.username=username
        user.first_name=first_name
        user.last_name=last_name
        user.email=email
        user.phone_number=phone_number
        user.save()
        return redirect('users')
    else:
        return render(request,'glam_admin/edit_user.html',{'user':user})

# Admin block/unblock user
@login_required(login_url='admin-login') 
def block_unblock_user(request,pk):
    user=UserAccount.objects.get(pk=pk)
    if user.is_active:
        user.is_active=False
    else:
        user.is_active=True
    user.save()
    return redirect('users')

@login_required(login_url='user-login')
def my_orders(request):
    query=request.GET.get('q')
    if query:
        ordered_products=OrderProduct.objects.filter(
            Q(product__product_name__icontains=query) |
            Q(order__status__icontains=query),
            user=request.user, 
            ordered=True
        ).order_by('-created_at')
    else:
        ordered_products=OrderProduct.objects.filter(user=request.user, ordered=True).order_by('-created_at')
    grouped_orders = {}
    for product in ordered_products:
        order_number=product.order.order_number
        if order_number not in grouped_orders:
            grouped_orders[order_number]=[]
        grouped_orders[order_number].append(product)
    context={
        'ordered_products':ordered_products,
        'grouped_orders':grouped_orders,
    }
    return render(request,'glam_user/my_orders.html', context)

@login_required(login_url='user-login')  
def order_detail(request,order_id):
    order_detail=OrderProduct.objects.filter(order__order_number=order_id)
    order=Order.objects.get(order_number=order_id)
    existing_return_request = ReturnRequest.objects.filter(order=order).first()
    subtotal=0
    for i in order_detail:
        subtotal=subtotal+i.product_price * i.quantity
    context={
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal,
        'existing_return_request': existing_return_request,
        'discount': order.discount if order.discount else 0
    }
    return render(request,'glam_user/order_detail.html', context)

# user cancel an order
@login_required(login_url='user-login')
def cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if order.status == 'Delivered':
        messages.error(request, "You cannot cancel an order that has been delivered.")
        return redirect('order-detail', order_id=order_number)
    else:
        if order.payment.payment_method != 'cod':
            if order.payment and order.payment.status=='COMPLETED':
                user_wallet, created=Wallet.objects.get_or_create(user=request.user)
                refunded_amount=order.order_total - order.delivery_charge
                user_wallet.balance += refunded_amount
                user_wallet.save()

                WalletTransaction.objects.create(wallet=user_wallet, amount=refunded_amount, description=f"Refund for cancelled order #{order.order_number}")
                order.status = 'Cancelled'
                order.save()
                order.payment.status='REFUNDED'
                order.payment.save()
                messages.success(request, "Your order has been cancelled successfully. And the amount is credited to your wallet")
                return redirect('order-detail', order_id=order_number)
            else:
                return redirect('order-detail', order_id=order_number)

        else:
            return redirect('order-detail', order_id=order_number)

# User request for returning the delivered order
@login_required(login_url='user-login')
def request_return(request, order_number):
    if request.method == 'POST':
        order=get_object_or_404(Order,order_number=order_number, user=request.user)
        if order.status == 'Delivered':
            reason = request.POST.get('reason')
            existing_return_request = ReturnRequest.objects.filter(order=order).first()
            if existing_return_request:
                if existing_return_request.status == 'Approved' or existing_return_request.status == 'Rejected':
                    messages.error(request, "You cannot submit a return request for an order that has already been approved or rejected for return.")
                else:
                    messages.info(request, "You already have a return request submitted")
            else:
                return_request = ReturnRequest.objects.create(order=order, reason=reason)
                messages.success(request, "Your return request has been submitted.")
        else:
            messages.error(request, "You cannot return an order that has not delivered.")
    return redirect('order-detail', order_id=order_number)

# User withdraw the return request
@login_required(login_url='user-login')
def withdraw_return_request(request,order_number):
    order=get_object_or_404(Order,order_number=order_number, user=request.user)
    existing_return_request = ReturnRequest.objects.filter(order=order).first()
    if existing_return_request and existing_return_request.status != 'Approved':
        existing_return_request.delete()
        messages.success(request, "Your return request has been withdrawn.")
    else:
        messages.error(request, "You cannot withdraw an approved return request.")
    return redirect('order-detail', order_id=order_number)

@login_required(login_url='user-login')
def manage_address(request):
    addresses=UserAddress.objects.filter(user=request.user, is_deleted=False).order_by('-created_at')
    context={
        'addresses':addresses
    }
    return render(request,'glam_user/manage_address.html', context)

@login_required(login_url='user-login')
def add_new_address(request):
    if request.method=='POST':
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

        # Set all existing addresses to not default
        UserAddress.objects.filter(user=request.user, is_deleted=False).update(is_default=False)

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
            is_default=True
            )
        new_address.save()
        return redirect('manage-address')
    else:
        pass

@login_required(login_url='user-login')
def get_address_details(request, address_id):
    try:
        address = UserAddress.objects.get(id=address_id)
        data = {
            'first_name': address.first_name,
            'last_name': address.last_name,
            'email': address.email,
            'phone_number': address.phone_number,
            'address_line1': address.address_line1,
            'address_line2': address.address_line2,
            'country': address.country,
            'state': address.state,
            'city': address.city,
            'zip_code': address.zip_code,
        }
        return JsonResponse(data)
    except UserAddress.DoesNotExist:
        return JsonResponse({'error': 'Address not found'}, status=404)

@login_required(login_url='user-login')  
def edit_address(request, address_id):
    address = get_object_or_404(UserAddress, id=address_id)
    if request.method== 'POST':
        address.first_name = request.POST.get('first_name')
        address.last_name = request.POST.get('last_name')
        address.email = request.POST.get('email')
        address.phone_number = request.POST.get('phone_number')
        address.address_line1 = request.POST.get('address_line1')
        address.address_line2 = request.POST.get('address_line2')
        address.country = request.POST.get('country')
        address.state = request.POST.get('state')
        address.city = request.POST.get('city')
        address.zip_code = request.POST.get('zip_code')

        address.save()
        return redirect('manage-address') 

    return render(request,'glam_user/manage_address.html',{'address':address})

@login_required(login_url='user-login')
def delete_address(request, address_id):
    address = get_object_or_404(UserAddress, id=address_id)
    address.is_deleted=True
    address.save()
    return redirect('manage-address')

@login_required(login_url='user-login')
def profile_information(request):
    user=request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    if request.method=='POST':
        user_form=UserForm(request.POST, instance=user)
        profile_form=UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated')
            return redirect('profile-information')
    else:
        user_form=UserForm(instance=user)
        profile_form=UserProfileForm(instance=user_profile)
    return render(request,'glam_user/profile.html',{'user_form':user_form,'profile_form':profile_form})

@login_required(login_url='user-login')
def change_password(request):
    user=request.user
    if request.method=='POST':
        old_password=request.POST['old_password']
        new_password=request.POST['new_password']
        retype_password=request.POST['retype_password']
        if check_password(old_password, user.password):
            if new_password != retype_password:
                messages.error(request,"Password do not match")
                return render(request,'glam_user/change_password.html')
            elif check_password(new_password, user.password):
                messages.error(request,"Please enter a new password")
                return render(request,'glam_user/change_password.html')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request,"Password changed successfully")
                return render(request,'glam_user/change_password.html')
        else:
            messages.error(request,"Entered password does not match with your account password")
            return render(request,'glam_user/change_password.html')
    else:
        return render(request,'glam_user/change_password.html')

@login_required(login_url='user-login')   
def my_wallet(request):
    user_wallet=get_object_or_404(Wallet, user=request.user)
    user_transactions=user_wallet.transactions.all().order_by('-timestamp')
    context={
        'user_wallet':user_wallet,
        'user_transactions':user_transactions,
    }
    return render(request,'glam_user/my_wallet.html',context)

@login_required(login_url='user-login')
def wishlist(request):
    wishlist = WishList.objects.filter(user=request.user)
    context={
        'wishlist':wishlist
    }
    return render(request,'glam_user/wishlist.html', context)

@login_required(login_url='user-login')
def add_wishlist(request):
    pid=request.GET['product']
    product=Product.objects.get(id=pid)
    data={}
    check_wishlist=WishList.objects.filter(product=product,user=request.user).count()
    if check_wishlist > 0:
        data={
            'bool':False
        }
    else:
        wishlist=WishList.objects.create(product=product,user=request.user)
        data={
            'bool':True
        }
    return JsonResponse(data)

@login_required(login_url='user-login')
def remove_wishlist(request, product_id):
    wishlist_item=get_object_or_404(WishList, user=request.user, product_id=product_id)
    wishlist_item.delete()
    return redirect('wishlist')

@login_required(login_url='user-login')
def referral(request):
    user_profile=UserProfile.objects.get(user=request.user)
    applied_referral_code = None

    if user_profile.referred_by:
        referred_user_profile = user_profile.referred_by.userprofile
        applied_referral_code = referred_user_profile.referral_code
    context={
        'user_profile':user_profile,
        'applied_referral_code':applied_referral_code,
    }
    return render(request, 'glam_user/referral.html', context)

@login_required(login_url='user-login')
def apply_referral(request):
    if request.method=='POST':
        referral_code=request.POST.get('referral_code')
        try:
            referred_user_profile=UserProfile.objects.get(referral_code=referral_code)
        except UserProfile.DoesNotExist:
            messages.error(request,'Invalid referral code')
            return redirect('referral')
        
        current_user_profile=UserProfile.objects.get(user=request.user)
        
        if current_user_profile == referred_user_profile:
            messages.error(request,'You cannot apply your own code')
            return redirect('referral')
        
        if current_user_profile.referred_by:
            messages.error(request,'You have already applied a referral code')
            return redirect('referral')
        
        current_user_profile.referred_by=referred_user_profile.user
        current_user_profile.save()

        current_user_wallet=Wallet.objects.get(user=request.user)
        referred_user_wallet=Wallet.objects.get(user=referred_user_profile.user)

        bonus_amount=50

        current_user_wallet.balance += bonus_amount
        current_user_wallet.save()

        referred_user_wallet.balance += bonus_amount
        referred_user_wallet.save()

        WalletTransaction.objects.create(wallet=current_user_wallet, amount=bonus_amount, description=f'Bonus for referring user {referred_user_profile.user.username}')
        WalletTransaction.objects.create(wallet=referred_user_wallet, amount=bonus_amount, description=f'Bonus for applying referral code of {request.user.username}')
        applied_referral_code = referred_user_profile.referral_code

        messages.success(request, 'Referral code applied successfully, 50 bonus amount credited')

        return render(request, 'glam_user/referral.html', {'applied_referral_code': applied_referral_code})
    return redirect('referral')

@csrf_exempt
@login_required(login_url='user-login')
def continue_paypal_payments(request):
    body=json.loads(request.body)
    order=Order.objects.get(user=request.user, is_ordered=True, order_number=body['orderID'])
    
    # Updating payment table
    payment=Payment.objects.get(user=request.user, order=order)
    payment.user=request.user
    payment.payment_id=body['transID']
    payment.payment_method = body['payment_method']
    payment.amount_paid = order.order_total
    payment.status=body['status']
    payment.save()

    order.payment=payment
    order.save()
   
    orderproduct=OrderProduct.objects.filter(user=request.user, order=order)
    for item in orderproduct:
        orderproduct.payment=payment
        orderproduct.save()

    order.status='Ordered'
    order.save()
    # Send order number and transaction id back to sendData method via json response
    data={
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

@login_required(login_url='user-login')
def continue_paypal_order_complete(request):
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
        return render(request,'glam_user/order_detail.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('user-home')
