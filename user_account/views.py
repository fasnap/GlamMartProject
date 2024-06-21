from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from . forms import RegistrationForm
from . models import UserAccount,OTP
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from store.models import Product
from category.models import Category
from carts.models import Cart,CartItem
from carts.views import _cart_id
import requests
from django.db.models import Count, Avg
from coupons.models import Coupons

# Create your views here.
@never_cache
def user_home(request):
    products=Product.objects.all().order_by('-created_at')[:8]
    categories=Category.objects.all().order_by('created_at')[:1]
    all_categories = Category.objects.annotate(product_count=Count('product')).order_by('id')[1:5]
    coupon=Coupons.objects.filter(status=True).order_by('-discount').first()
    max_order_products=Product.objects.all().annotate(num_orders=Count('orderproduct')).order_by('-num_orders')[:3]
    top_rated_products=Product.objects.annotate(avg_rating=Avg('reviewrating__rating')).order_by('-avg_rating')[:3]
    newest_products=Product.objects.all().order_by('-created_at')[:3]
    slide_categories=Category.objects.all()
    context={
        'products':products,
        'max_order_products':max_order_products,
        'categories':categories,
        'all_categories':all_categories,
        'top_rated_products':top_rated_products,
        'newest_products':newest_products,
        'coupon':coupon,
        'slide_categories':slide_categories,
    }
    return render(request,'glam_user/index.html',context)

@never_cache
def user_login(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('user-home')
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user = authenticate(email=email,password=password)
        if user is not None and not user.is_superuser:
            try:
                cart=Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists=CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart)
                    product_variation=[]
                    for item in cart_item:
                        variation=item.variations.all()
                        product_variation.append(list(variation))
                    
                    cart_item=CartItem.objects.filter(user=user)
                    ex_var_list=[]
                    id=[]
                    for item in cart_item:
                        existing_variation=item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index=ex_var_list.index(pr)
                            item_id=id[index]
                            item=CartItem.objects.get(id=item_id)
                            item.quantity+=1
                            item.user=user
                            item.save()
                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user=user
                                item.save()
            except:
               pass
               
            login(request,user)
            # Checkout page into login page from there cart page
            url=request.META.get('HTTP_REFERER')
            try:
                query=requests.utils.urlparse(url).query
               
                #next=/cart/checkout/
                params=dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page=params['next']
                    return redirect(next_page)
            except:
                return redirect('user-home')     
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('user-login')
    else:
        return render(request,'glam_user/login.html')

@login_required(login_url='user-login')
def user_logout(request):
    logout(request)
    return redirect('user-login')

def user_register(request):
    if request.user.is_authenticated:
        return redirect('user-home')
    if request.method=='POST':
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            phone_number=form.cleaned_data['phone_number']
            password=form.cleaned_data['password']
            # Generate OTP
            otp = get_random_string(length=6, allowed_chars='1234567890')
            
            user=UserAccount.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,phone_number=phone_number,password=password)
            user.save()
            # After saving the user, you can create an OTP object and associate it with the user
            otp_instance = OTP.objects.create(user=user, otp=otp, created_at=timezone.now())
             
            print(otp)
            # Send OTP to user's email
            send_mail(
                'OTP for Registration',
                f'Your OTP is: {otp}',
                'testmaildjango27121995@gmail.com',
                [email],
                fail_silently=False,
            )
            return redirect('verify_otp', otp_id=otp_instance.id)
    else:
        form=RegistrationForm()
    context={
        'form':form,
        'form_errors':form.errors if request.method == 'POST' else None
    }
    return render(request, 'glam_user/register.html',context)

def verify_otp(request, otp_id):
    otp_obj = get_object_or_404(OTP, id=otp_id)
    expire_time=otp_obj.created_at+timezone.timedelta(minutes=1)
    if request.method=='POST':
        otp_entered = request.POST.get('otp')
        if not otp_entered:
            otp_error = True
            return render(request, 'glam_user/verify_otp.html',{'otp_error':otp_error, 'otp_id': otp_id})
        elif timezone.now() > expire_time:
            messages.error(request,"Otp Expired Please click resend otp for new otp")
            return render(request, 'glam_user/verify_otp.html',{'otp_id': otp_id})
        elif otp_entered == otp_obj.otp:
            otp_obj.delete()
            user = otp_obj.user
            user.is_active = True
            user.save()
            return redirect('user-login')
        else:
            messages.error(request,"Invalid OTP. Please enter the correct OTP")
            return render(request, 'glam_user/verify_otp.html',{'otp_id': otp_id})
    else:
        messages.success(request,'Otp send succesfully!!!')
        return render(request, 'glam_user/verify_otp.html',{'otp_id': otp_id})

def resend_otp(request, otp_id):
    try:
        otp_instance=OTP.objects.get(id=otp_id)
        expire_time=otp_instance.created_at+timezone.timedelta(minutes=1)

        if timezone.now()>expire_time:
            new_otp=get_random_string(length=6, allowed_chars='1234567890')
            otp_instance.otp=new_otp
            otp_instance.created_at=timezone.now()
            otp_instance.save()

            send_mail(
                'New OTP for registration ',
                f'Your new OTP is: {new_otp}',
                'testmaildjango27121995@gmail.com',
                [otp_instance.user.email],
                fail_silently=False,
            )
            messages.success(request, 'New OTP has been sent to you mail.')

        else:
            messages.error(request,'OTP resend failed . OTP is still valid')
    except OTP.DoesNotExist:
         messages.error(request, 'Invalid OTP ID.')

    return redirect('verify_otp', otp_id=otp_id)


@never_cache
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if UserAccount.objects.filter(email=email).exists():
            user = UserAccount.objects.get(email=email)
            otp = get_random_string(length=6, allowed_chars='1234567890')
            try:
                otp_instance, created = OTP.objects.update_or_create(user=user,defaults={'otp': otp, 'created_at': timezone.now()})

                send_mail(
                    'Password Reset OTP',
                    f'Your OTP for password reset is: {otp}',
                    'testmaildjango27121995@gmail.com',
                    [email],
                    fail_silently=False,
                )

                messages.success(request, "OTP has been sent to your email address.")
                return redirect('verify_forgot_password_otp', otp_id=otp_instance.id)
            except Exception as e:
                messages.error(request, 'An error occurred while generating the OTP. Please try again.')
                return redirect('forgot-password')
        else:
            messages.error(request, 'No account found with this email address.')
            return redirect('forgot-password')
    return render(request, 'glam_user/forgot_password.html')

@never_cache
def verify_forgot_password_otp(request, otp_id):
    otp_obj = get_object_or_404(OTP, id=otp_id)
    expire_time = otp_obj.created_at + timezone.timedelta(minutes=1)

    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        if not otp_entered:
            otp_error = True
            return render(request, 'glam_user/verify_forgot_password_otp.html', {'otp_error': otp_error, 'otp_id': otp_id})
        elif timezone.now() > expire_time:
            messages.error(request, "OTP expired. Please request a new one.")
            return render(request, 'glam_user/verify_forgot_password_otp.html',{'otp_id': otp_id})
        elif otp_entered == otp_obj.otp:
            otp_obj.delete()
            request.session['reset_user_id'] = otp_obj.user.id 
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please enter the correct OTP.')
            return render(request, 'glam_user/verify_forgot_password_otp.html', {'otp_id': otp_id})
    else:
        return render(request, 'glam_user/verify_forgot_password_otp.html', {'otp_id': otp_id})

@never_cache
def resend_forgot_otp(request, otp_id):
    try:
        otp_instance = OTP.objects.get(id=otp_id)
        expire_time = otp_instance.created_at + timezone.timedelta(minutes=1)

        if timezone.now() > expire_time:
            new_otp = get_random_string(length=6, allowed_chars='1234567890')
            otp_instance.otp = new_otp
            otp_instance.created_at = timezone.now()
            otp_instance.save()

            send_mail(
                'New OTP for Password Reset',
                f'Your new OTP is: {new_otp}',
                'testmaildjango27121995@gmail.com',
                [otp_instance.user.email],
                fail_silently=False,
            )
            messages.success(request, 'New OTP has been sent to your email.')

        else:
            messages.error(request, 'OTP resend failed. OTP is still valid.')
    except OTP.DoesNotExist:
        messages.error(request, 'Invalid OTP ID.')

    return redirect('verify_forgot_password_otp', otp_id=otp_id)

@never_cache
def reset_password(request):
    if 'reset_user_id' not in request.session:
        messages.error(request, 'Session expired. Please request a new password reset.')
        return redirect('forgot-password')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            user_id = request.session['reset_user_id']
            user = UserAccount.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            del request.session['reset_user_id']
            messages.success(request, 'Password reset successful. You can now log in with your new password.')
            return redirect('user-login')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password')
    
    return render(request, 'glam_user/reset_password.html')