from django.shortcuts import render,redirect,get_object_or_404
from . models import Category,SubCategory
from django.utils.text import slugify
from django.db import IntegrityError
from django.contrib import messages
from store.models import Product
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# Admin view all categories .
@login_required(login_url='admin-login')
def category(request):
    query=request.GET.get('q')
    if query:
        categories=Category.objects.filter(category_name__icontains=query)
    else:
        categories=Category.objects.all()
    paginator=Paginator(categories, 10)
    page=request.GET.get('page')
    try:
        paged_categories=paginator.get_page(page)
    except PageNotAnInteger:
        paged_categories = paginator.page(1)
    except EmptyPage:
        paged_categories = paginator.page(paginator.num_pages)
    context={
        'categories':paged_categories,
        'query':query,
    }
    return render(request,'glam_admin/category.html', context)

# Admin add new categories
@login_required(login_url='admin-login')
def add_category(request):
    if request.method=='POST':
        category_name=request.POST['category_name']
        description=request.POST.get('description')
        category_offer=request.POST.get('category_offer')
        category_image=request.FILES.get('category_image')
        if not category_name:
            messages.error(request, "Category name is required.")
            return render(request, 'glam_admin/add_category.html')
        try:
            category_offer = float(category_offer)
        except ValueError:
            category_offer = 0
        slug = slugify(category_name)
        try:
            category=Category.objects.create(category_name=category_name,description=description,category_image=category_image,slug=slug, category_offer=category_offer)
            category.save()
            return redirect('category')
        except IntegrityError:
            messages.error(request,"Category name already exists")
            return render(request,'glam_admin/add_category.html')
        
    return render(request,'glam_admin/add_category.html')

# Admin edit category
@login_required(login_url='admin-login')
def edit_category(request,category_slug):
    category=Category.objects.get(slug=category_slug)
    if request.method=='POST':
        category_name=request.POST['category_name']
        category_offer=request.POST.get('category_offer')
        description=request.POST['description']
        if not category_name:
            messages.error(request, "Category name is required.")
            return render(request, 'glam_admin/edit_category.html',{'category':category})
        slug=slugify(category_name)
        try:
            category_offer = float(category_offer)
        except ValueError:
            category_offer = 0
        if 'category_image' in request.FILES:
            category_image=request.FILES['category_image']
        else:
            category_image=category.category_image
            
        category.category_name=category_name
        category.category_image=category_image
        category.description=description
        category.category_offer=category_offer
        category.slug=slug
        category.save()
        return redirect('category')
    else:
        return render(request, 'glam_admin/edit_category.html', {'category':category})

# Admin activate/deactivate category
@login_required(login_url='admin-login')
def activate_inactivate_category(request,category_slug):
    category=Category.objects.get(slug=category_slug)
    products=Product.objects.filter(category=category)
    if category.is_active:
        category.is_active=False
        products.update(is_available=False)
    else:
        category.is_active=True
        products.update(is_available=True)
    category.save()
    return redirect('category')

# Admin view all sub categories
@login_required(login_url='admin-login')
def sub_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    sub_categories = SubCategory.objects.filter(category=category)
    context={
        'sub_categories':sub_categories,
        'category': category,
        'category_slug': category_slug,
    }
    return render(request,'glam_admin/subcategory.html', context)

# Admin add new sub categories
@login_required(login_url='admin-login')
def add_subcategory(request,category_slug):
    if request.method=="POST":
        sub_category_name=request.POST['sub_category_name']
        description=request.POST['description']
        subcategory_offer=request.POST.get('subcategory_offer',0)
        sub_category_image=request.FILES.get('sub_category_image')
        category = Category.objects.get(slug=category_slug)
        sub_category_slug_name=sub_category_name + ' ' + category.category_name
        slug= slugify(sub_category_slug_name)
        try:
            subcategory_offer = float(subcategory_offer)
        except ValueError:
            subcategory_offer = 0
        sub_category=SubCategory.objects.create(sub_category_name=sub_category_name,description=description,sub_category_image=sub_category_image,slug=slug,category=category, subcategory_offer=subcategory_offer)
        sub_category.save()
        return redirect('sub-category',category_slug=category_slug)
    else:
        return render(request,'glam_admin/add_subcategory.html', {'category_slug': category_slug})

# Admin edit sub categories   
@login_required(login_url='admin-login')
def edit_subcategory(request,subcategory_slug):
    sub_category=get_object_or_404(SubCategory,slug=subcategory_slug)
    if request.method=='POST':
        sub_category_name=request.POST['sub_category_name']
        description=request.POST['description']
        subcategory_offer=request.POST.get('subcategory_offer')
        slug = slugify(sub_category_name + ' ' + sub_category.category.category_name)
        if 'sub_category_image' in request.FILES:
            sub_category_image=request.FILES['sub_category_image']
        else:
            sub_category_image=sub_category.sub_category_image
        try:
            subcategory_offer = float(subcategory_offer)
        except ValueError:
            subcategory_offer = 0
        sub_category.sub_category_name=sub_category_name
        sub_category.sub_category_image=sub_category_image
        sub_category.description=description
        sub_category.subcategory_offer=subcategory_offer
        sub_category.slug=slug
        sub_category.save()
        return redirect('sub-category',category_slug=sub_category.category.slug)
    else:
        return render(request, 'glam_admin/edit_subcategory.html', {'sub_category':sub_category})

# Admin activate/deactivate sub category 
@login_required(login_url='admin-login')
def activate_inactivate_subcategory(request,subcategory_slug):
    sub_category=get_object_or_404(SubCategory,slug=subcategory_slug)
    products=Product.objects.filter(sub_category=sub_category)
    if sub_category.is_active:
        sub_category.is_active=False
        products.update(is_available=False)
    else:
        sub_category.is_active=True
        products.update(is_available=True)
    sub_category.save()
    return redirect('sub-category',category_slug=sub_category.category.slug)

