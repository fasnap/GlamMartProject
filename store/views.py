from django.shortcuts import render,redirect
from category.models import Category,SubCategory
from orders.models import OrderProduct
from . models import Product,Variation
from django.utils.text import slugify
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import ReviewRating
from carts.models import CartItem,Cart
from carts.views import _cart_id
from django.http import JsonResponse
from django.db.models.functions import Lower
from django.db.models import Count
from . forms import ReviewForm
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required

# Admin side product list
@login_required(login_url='admin-login')
def product(request):
    query=request.GET.get('q')
    if query:
        products=Product.objects.filter(product_name__icontains=query)
    else:
        products=Product.objects.all()

    paginator=Paginator(products, 10)
    page=request.GET.get('page')
    try:
        paged_products=paginator.get_page(page)
    except PageNotAnInteger:
        paged_products = paginator.page(1)
    except EmptyPage:
        paged_products = paginator.page(paginator.num_pages)
    context={
        'products':paged_products,
        'query':query,
    }
    return render(request,'glam_admin/product.html', context)

# Admin side add product
@login_required(login_url='admin-login')
def add_product(request):
    categories=Category.objects.filter(is_active=True)
    sub_categories=SubCategory.objects.filter(is_active=True)
    if request.method=='POST':
        product_name=request.POST['product_name']
        description=request.POST['description']
        actual_price=request.POST['actual_price']
        stock=request.POST['stock']
        product_image1=request.FILES.get('product_image1')
        product_image2=request.FILES.get('product_image2')
        product_image3=request.FILES.get('product_image3')
        category_id=request.POST['category']
        product_offer = request.POST['product_offer']
        sub_category_id=request.POST['sub_category']
       
        if not product_name or not description or not actual_price or not stock or not category_id or not sub_category_id:
            messages.error(request, "All fields are required.")
            return render(request, 'glam_admin/add_product.html', {'categories': categories, 'sub_categories': sub_categories})
        
        try:
            actual_price = float(actual_price)
        except ValueError:
            messages.error(request, "Actual price must be a number.")
            return render(request, 'glam_admin/add_product.html', {'categories': categories, 'sub_categories': sub_categories})
        try:
            stock = int(stock)
        except ValueError:
            messages.error(request, "Stock must be an integer.")
            return render(request, 'glam_admin/add_product.html', {'categories': categories, 'sub_categories': sub_categories})
        try:
            product_offer = float(product_offer) if product_offer else 0
        except ValueError:
            messages.error(request, "Product offer must be a number.")
            return render(request, 'glam_admin/add_product.html', {'categories': categories, 'sub_categories': sub_categories})

        if not (product_image1 and product_image2 and product_image3):
            messages.error(request, "Please upload all three product images.")
            return render(request, 'add_product.html')
        
        category=Category.objects.get(id=category_id)
        sub_category=SubCategory.objects.get(id=sub_category_id)
        slug=slugify(product_name)

        category_offer=category.category_offer if category.category_offer else 0
        subcategory_offer=sub_category.subcategory_offer if sub_category.subcategory_offer else 0

        final_offer=max(category_offer, subcategory_offer, product_offer)

        offer_price=actual_price-(actual_price*(final_offer/100))

       
        product=Product.objects.create(product_name=product_name,description=description,actual_price=actual_price,offer=final_offer,product_offer=product_offer,stock=stock,category=category,offer_price=offer_price,sub_category=sub_category,slug=slug,product_image1=product_image1,product_image2=product_image2,product_image3=product_image3)
        if int(stock) <=0:
            product.is_available=False
        product.save()
        return redirect('product')
    context={
        'categories':categories,
        'sub_categories':sub_categories,
    }
    return render(request,'glam_admin/add_product.html',context)

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'sub_category_name')
    return JsonResponse({'subcategories': list(subcategories)})

# Admin side edit product
@login_required(login_url='admin-login')
def edit_product(request,product_slug):
    product=Product.objects.get(slug=product_slug)
    categories=Category.objects.filter(is_active=True)
    sub_categories=SubCategory.objects.filter(is_active=True)
    if request.method=='POST':
        product_name=request.POST['product_name']
        description=request.POST['description']
        stock=request.POST['stock']
        actual_price=float(request.POST['actual_price'])
        product_offer=float(request.POST['product_offer'])
        category_id=request.POST['category']
        category = Category.objects.get(id=category_id)
        sub_category_id=request.POST['sub_category']
        sub_category = SubCategory.objects.get(id=sub_category_id)
        slug=slugify(product_name)

        if 'product_image1' in request.FILES:
            product_image1=request.FILES['product_image1']
        else:
            product_image1=product.product_image1

        if 'product_image2' in request.FILES:
            product_image2=request.FILES['product_image2']
        else:
            product_image2=product.product_image2

        if 'product_image3' in request.FILES:
            product_image3=request.FILES['product_image3']
        else:
            product_image3=product.product_image3

        product.product_name=product_name
        product.product_image1=product_image1
        product.product_image2=product_image2
        product.product_image3=product_image3
        product.description=description
        product.stock=stock
        product.actual_price=actual_price
        product.product_offer=product_offer

        category_offer=category.category_offer if category.category_offer else 0
        subcategory_offer=sub_category.subcategory_offer if sub_category.subcategory_offer else 0
       
        final_offer=max(category_offer, subcategory_offer, product_offer)
        offer_price=actual_price-(actual_price*(final_offer/100))
        product.offer=final_offer
        product.offer_price=offer_price
        product.slug=slug
        product.category=category
        product.sub_category=sub_category
        if int(stock) <=0:
            product.is_available=False
        product.save()
        return redirect('product')
    else:
        context={
            'categories':categories,
            'sub_categories':sub_categories,
            'product':product
        }
        return render(request, 'glam_admin/edit_product.html',context)

# Admin side activate/deactivate product
@login_required(login_url='admin-login')
def activate_inactivate_product(request,product_slug):
    product=Product.objects.get(slug=product_slug)
    order_product=OrderProduct.objects.filter(product=product)
    if product.is_available:
        product.is_available=False

        for item in order_product:
            order=item.order
            if order.status != 'Cancelled':
                order.status='Cancelled'
                order.save()
        messages.success(request, f"The product '{product.product_name}' has been deactivated and related orders have been cancelled.")
    else:
        product.is_available=True
        messages.success(request, f"The product '{product.product_name}' has been activated.")
    product.save()
    return redirect('product')

def store(request, category_slug=None, sub_category_slug=None):
    categories=None
    products=None
    sub_categories=None
    product_count = 0 
    query=request.GET.get('q')
    sort_by = request.GET.get("sort", "nf") 
    color_values = request.GET.getlist('colors')
    size_values = request.GET.getlist('sizes')
    products = Product.objects.all()
    sizes= Variation.objects.filter(variation_category='size', is_active=True).values_list('variation_value', flat=True).distinct()
    colors= Variation.objects.filter(variation_category='color', is_active=True).values_list('variation_value', flat=True).distinct()

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    try: 
        min_price=int(min_price) if min_price else None
        max_price=int(max_price) if max_price else None
    except ValueError:
        min_price=None
        max_price=None

    if category_slug  !=  None and sub_category_slug == None:
        categories=get_object_or_404(Category, slug=category_slug)
        products=products.filter(category=categories)
    elif category_slug  !=  None and sub_category_slug != None :
        categories=get_object_or_404(Category, slug=category_slug)
        sub_categories=get_object_or_404(SubCategory, slug=sub_category_slug)
        products=products.filter(category=categories,sub_category=sub_categories)

    
    if query:
        products=products.filter(product_name__icontains=query)
    if size_values:
        products=products.filter(variation__variation_category='size', variation__variation_value__in=size_values)
    if color_values:
        products=products.filter(variation__variation_category='color', variation__variation_value__in=color_values)
    if min_price is  not None and max_price is not None:
        products=products.filter(offer_price__range=(min_price,max_price))
    if size_values and color_values:
        products=products.filter(Q(variation__variation_category='size', variation__variation_value__in=size_values) | Q(variation__variation_category='color', variation__variation_value__in=color_values))
    
    if sort_by == "l2h":
        products=products.distinct().order_by("offer_price")
    elif sort_by == "h2l":
        products=products.distinct().order_by("-offer_price")
    elif sort_by == "nf":
        products=products.distinct().order_by("-created_at")
    elif sort_by == "a2z":
        products=products.distinct().order_by(Lower("product_name"))
    elif sort_by == "z2a":
        products=products.distinct().order_by(Lower("product_name").desc())
    elif sort_by == "popular":
        products=products.annotate(num_orders=Count('orderproduct')).distinct().order_by('-num_orders')
    
    paginator=Paginator(products, 9)
    page=request.GET.get('page')
    paged_products=paginator.get_page(page)
    
    product_count=products.count()
    context={
        'products':paged_products,
        'product_count':product_count,
        'query': query,
        'sort_by': sort_by,
        'sizes':sizes,
        'colors':colors,
        'selected_colors':color_values,
        'selected_sizes':size_values,
        
    }
    return render(request,'glam_user/store.html',context)

def product_detail(request,category_slug,sub_category_slug,product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug,sub_category__slug=sub_category_slug,slug=product_slug)
        related_products=Product.objects.filter(sub_category=product.sub_category).exclude(slug=product_slug)[:4]
        in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=product).exists()
    except Exception as e:
        raise e
    if request.user.is_authenticated:
        try:
            orderproduct=OrderProduct.objects.filter(user=request.user, product_id=product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct=None
    else:
        orderproduct=None
    reviews=ReviewRating.objects.filter(product_id=product.id, status=True)
    context={
        'product':product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        'related_products':related_products,
    }
    return render(request,'glam_user/product-detail.html',context)

@login_required(login_url='user-login')
def submit_review(request,product_id):
    url=request.META.get('HTTP_REFERER') #store the previous url
    if request.method=='POST':
        try:
            reviews=ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form=ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request,"Thank You! Your review has been updated successfully")
            return redirect(url)
        except ReviewRating.DoesNotExist: 
            form=ReviewForm(request.POST)
            if form.is_valid():
                data=ReviewRating()
                data.subject=form.cleaned_data['subject']
                data.rating=form.cleaned_data['rating']
                data.review=form.cleaned_data['review']
                data.ip=request.META.get("REMOTE_ADDR")
                data.product_id=product_id
                data.user_id=request.user.id
                data.save()
                messages.success(request,"Thank You! Your review submitted")
                return redirect(url)

# Admin side view all variations
@login_required(login_url='admin-login')          
def variations(request):
    query=request.GET.get('q')
    if query:
        variations=Variation.objects.filter(Q(product__product_name__icontains=query) | Q(variation_category__icontains=query) | Q(variation_value__icontains=query))
    else:
        variations=Variation.objects.all()
    
    paginator=Paginator(variations, 10)
    page=request.GET.get('page')
    try:
        paged_variations=paginator.get_page(page)
    except PageNotAnInteger:
        paged_variations = paginator.page(1)
    except EmptyPage:
        paged_variations = paginator.page(paginator.num_pages)
    context={
        'variations':paged_variations,
        'query':query,
    }
    return render(request,'glam_admin/variations.html', context)

# Admin side add variations
@login_required(login_url='admin-login') 
def add_variation(request):
    if request.method=='POST':
        product_id=request.POST['product']
        variation_category=request.POST['variation_category']
        variation_value=request.POST['variation_value']
        variation_exists=Variation.objects.filter(product_id=product_id,variation_category__iexact=variation_category,variation_value__iexact=variation_value).exists()
        if variation_exists:
            messages.error(request,'Variation already exists')
            return redirect('add-variation')
        product=get_object_or_404(Product, id=product_id)
        variation=Variation.objects.create(product=product,variation_category=variation_category,variation_value=variation_value)
        variation.save()
        return redirect('variations')
    else:
        products=Product.objects.all()
        variations_categories=Variation.variation_category_choice
        print(variations_categories)
        context={
            'products':products,
            'variations_categories':variations_categories,
        }
        return render(request,'glam_admin/add_variation.html',context)

# Admin side edit variation
@login_required(login_url='admin-login')   
def edit_variation(request, variation_id):
    variation=Variation.objects.get(id=variation_id)
    if request.method=='POST':
        product_id=request.POST['product']
        variation_category=request.POST['variation_category']
        variation_value=request.POST['variation_value']
        variation_exists=Variation.objects.filter(product_id=product_id,variation_category__iexact=variation_category,variation_value__iexact=variation_value).exists()
        if variation_exists:
            messages.error(request,'Variation already exists')
            return redirect('edit_variation', variation_id=variation.id)
        product=get_object_or_404(Product, id=product_id)
        variation.product=product
        variation.variation_category=variation_category
        variation.variation_value=variation_value
        variation.save()
        return redirect('variations')
    else:
        products=Product.objects.exclude(id=variation.product.id)
        variations_categories=Variation.objects.values('variation_category').distinct()
        context={
            'products':products,
            'variation':variation,
            'variations_categories':variations_categories,
        }
        return render(request,'glam_admin/edit_variation.html',context)

# Admin side activate/deactivate variations
@login_required(login_url='admin-login')  
def activate_inactivate_variation(request, variation_id):
    variation=Variation.objects.get(id=variation_id)
    if variation.is_active:
        variation.is_active=False
    else:
        variation.is_active=True
    variation.save()
    return redirect('variations')