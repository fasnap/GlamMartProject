#admin view all coupons
from django.contrib import messages
from django.http.response import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from datetime import date
from coupons.forms import CouponApplyForm
from .models import Coupons
from .models import CouponCheck
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth.decorators import login_required

def checkCoupon(request, discount=0):
    if 'coupon_id' in request.session:
        del request.session['sub_total']
        del request.session['coupon_id']
        del request.session['discount_price']
    flag = 0
    discount_price = 0
    coupon = request.POST['coupon']
    total = float(request.POST['total'])
    if Coupons.objects.filter(code=coupon).exists():
        coup = Coupons.objects.get(code=coupon)
        if coup.status == True:
            flag = 1
            if not CouponCheck.objects.filter(user=request.user, coupon=coup):
                discount_price = total*int(coup.discount)/100
                total = total-(total*int(coup.discount)/100)
                flag = 2
                request.session['sub_total'] = total
                request.session['coupon_id'] = coup.id
                request.session['discount_price'] = discount_price
    data = {
        'total': total,
        'flag': flag,
        'discount_price': discount_price,
    }
    return JsonResponse(data)

# Admin coupons listing
@login_required(login_url='admin-login')
def coupons(request):
    query=request.GET.get('q')
    if query:
        coupons = Coupons.objects.filter(
            Q(code__icontains=query) | 
            Q(coupon_name__icontains=query) |
            Q(discount__icontains=query) 
        )
    else:
        coupons = Coupons.objects.all()
    today = date.today()
    for coupon in coupons:
        if coupon.valid_from <= today and coupon.valid_to >= today:
            Coupons.objects.filter(id=coupon.id).update(status=True)
        else:
            Coupons.objects.filter(id=coupon.id).update(status=False)
    context = {
        'coupons': coupons
    }
    return render(request,'glam_admin/coupons.html',context)

#admin delete coupon
@login_required(login_url='admin-login')
def delete_coupon(request,id):
    Coupons.objects.filter(id=id).delete()
    return redirect('coupons')

#admin edit coupon
@login_required(login_url='admin-login')
def edit_coupon(request,id):
    coupon = get_object_or_404(Coupons, id=id)
    today = date.today() 
    if request.method == 'POST':
        form=CouponApplyForm(request.POST,request.FILES,instance=coupon)
        if form.is_valid():
            new_code = form.cleaned_data['code']
            discount = form.cleaned_data['discount']
            if int(discount) < 0:
                messages.error(request, "Coupon discount cannot be negative")
                return render(request, 'glam_admin/edit_coupon.html', {'coupon': coupon, 'form': form})
            if Coupons.objects.filter(code=new_code).exclude(id=coupon.id).exists():
                messages.error(request, "Coupon code already exists")
                return render(request, 'glam_admin/edit_coupon.html', {'coupon': coupon, 'form': form})
            coupon = form.save(commit=False)
            if coupon.valid_from <= today and coupon.valid_to >= today and coupon.valid_from <= coupon.valid_to:
                coupon.status = True
                coupon.save()
            else:
                messages.error(request, "Please Enter a correct date range")
                return render(request, 'glam_admin/edit_coupon.html', {'coupon': coupon, 'form': form})
            
            return redirect('coupons')
        else:
            messages.error(request, "Invalid form submission")
    else:
        form=CouponApplyForm(instance=coupon)
    return render(request,'glam_admin/edit_coupon.html',{'coupon':coupon,'form':form})

#admin add coupon
@login_required(login_url='admin-login')
def add_coupon(request):
    form = CouponApplyForm()
    today = date.today() 
    if request.method == 'POST': 
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            discount = form.cleaned_data['discount']
            if int(discount) < 0:
                messages.error(request, "Coupon discount cannot be negative")
                return render(request, 'glam_admin/add_coupon.html', {'form': form})
            try:
                existing_coupons = Coupons.objects.filter(code=code)
                if existing_coupons.exists():
                    messages.error(request, "Coupon code already exists")
                else:
                    coupon = form.save(commit=False)
                    if coupon.valid_from <= today and coupon.valid_to >= today and coupon.valid_from <= coupon.valid_to:
                        coupon.status = True
                        coupon.save()
                    else:
                        messages.error(request, "Please Enter a correct date range")
                        return render(request, 'glam_admin/add_coupon.html', {'coupon': coupon, 'form': form})
                    
                    return redirect('coupons')
            except ObjectDoesNotExist:
                pass
        else:
            messages.error(request, "Invalid form submission")
   
    else:
        form = CouponApplyForm()
    context = {'form': form}
    return render(request, 'glam_admin/add_coupon.html', context)