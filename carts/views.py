from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,Variation
from . models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from users.models import UserAddress
from coupons.models import Coupons as Coupon
from django.db.models import Q

from django.http import JsonResponse
# Create your views here.

# private function for getting the session id as cart id or create a new session id 
def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
        # cart=request.session.session_key
    return cart

def add_cart(request, product_id):
    current_user=request.user
    product=Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variation=[]
        if request.method=='POST':
            for item in request.POST:
                key=item    # Variation category
                value=request.POST[key] # Variation value
                try:
                    variation=Variation.objects.get(product=product, variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists=CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item=CartItem.objects.filter(product=product, user=current_user)
            ex_var_list=[]
            id=[]
            for item in cart_item:
                existing_variation=item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variation in ex_var_list:
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item=CartItem.objects.get(product=product,id=item_id)
                item.quantity += 1
                item.save()
            else:
                item=CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
            
                item.save()
        else: 
            cart_item=CartItem.objects.create(product=product, user=current_user, quantity=1)
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')

    else:
        product_variation=[]
        if request.method=='POST':
            for item in request.POST:
                key=item    # Variation category
                value=request.POST[key] # Variation value
                try:
                    variation=Variation.objects.get(product=product, variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request)) # Get the cart using cart id present in the session
        except Cart.DoesNotExist:
            cart=Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
        is_cart_item_exists=CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exists:
            cart_item=CartItem.objects.filter(product=product, cart=cart)
            ex_var_list=[]
            id=[]
            for item in cart_item:
                existing_variation=item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            if product_variation in ex_var_list:
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item=CartItem.objects.get(product=product,id=item_id)
                item.quantity += 1
                item.save()
            else:
                item=CartItem.objects.create(product=product,quantity=1,cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
            
                item.save()
        else: 
            cart_item=CartItem.objects.create(product=product, cart=cart, quantity=1)
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')


def remove_cart_item(request,product_id,cart_item_id):
    product=get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        grand_total=0
        delivery_charge=0
        has_active_items=False
       
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart)
       
        for cart_item in cart_items:
            if not cart_item.product.is_available or cart_item.product.stock <= 0:
                cart_item.is_active = False
                cart_item.save()
            else:
                has_active_items = True
                total+=(cart_item.product.offer_price * cart_item.quantity)
                quantity+=cart_item.quantity
                cart_item.is_active = True
                cart_item.save()
        
        
        cart_items = CartItem.objects.filter(
            Q(user=request.user) if request.user.is_authenticated else Q(cart=cart)
        )
        if total<500 and total != 0 :
            delivery_charge=50
        grand_total=total+delivery_charge
        
        
    except ObjectDoesNotExist:
        pass
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'delivery_charge':delivery_charge,
        'grand_total':grand_total,
        'has_active_items':has_active_items,
    }
    return render(request,'glam_user/cart.html', context)

@login_required(login_url='user-login')
def checkout(request,total=0,quantity=0,cart_items=None):
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        del request.session['sub_total']
        del request.session['discount_price']

    try:
        grand_total=0
        delivery_charge=0
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart)
        for cart_item in cart_items:
            if not cart_item.product.is_available or cart_item.product.stock <= 0:
                cart_item.is_active = False
                cart_item.save()
            else:
                total += (cart_item.product.offer_price * cart_item.quantity)
                quantity += cart_item.quantity
        if total<500 and total!=0:
            delivery_charge=50
        grand_total=total+delivery_charge
    except ObjectDoesNotExist:
        pass
    addresses=UserAddress.objects.filter(user=request.user)
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'delivery_charge':delivery_charge,
        'grand_total':grand_total,
        'addresses':addresses,
    }
    return render(request,'glam_user/checkout.html',context)


def increment_cart_item(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart_item_id = request.POST.get('cart_item_id')
        if request.user.is_authenticated:
            cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
        if cart_item.product.stock > cart_item.quantity:
            cart_item.quantity += 1
            cart_item.save()
            response = {'status': 'success', 'quantity': cart_item.quantity, 'item_total': cart_item.product.offer_price * cart_item.quantity}
        else:
            response = {'error':'Not enough stock'}
        return JsonResponse(response)
    
def decrement_cart_item(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart_item_id = request.POST.get('cart_item_id')
        if request.user.is_authenticated:
            cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            return JsonResponse({'quantity': cart_item.quantity, 'item_total': cart_item.product.offer_price * cart_item.quantity})
        else:
            cart_item.delete()
            return JsonResponse({'quantity': 0, 'item_total': 0})

def get_cart_totals(request):
    cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    total = 0
    delivery_charge = 0
    has_active_items = cart_items.exists()

    for cart_item in cart_items:
        total += cart_item.product.offer_price * cart_item.quantity

    if total < 500 and total > 0:
        delivery_charge = 50  # Example fixed delivery charge

    grand_total = total + delivery_charge
    response = {
        'total': total,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
        'has_active_items': has_active_items,
    }
    return JsonResponse(response)


