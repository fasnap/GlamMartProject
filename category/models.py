from django.db import models
from django.urls import reverse

# Model for category
class Category(models.Model):
    category_name=models.CharField(max_length=100, unique=True)
    slug=models.SlugField(unique=True)
    description=models.TextField(max_length=100, blank=True)
    category_image=models.ImageField(upload_to='photos/category', blank=True)
    category_offer=models.FloatField(default=0,null=True, blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name='Category'
        verbose_name_plural='Categories'

    def get_url(self):
        return reverse('product-by-category', args=[self.slug])

    def __str__(self):
        return self.category_name

# Model for sub category
class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    sub_category_name=models.CharField(max_length=100)
    slug=models.SlugField(unique=True)
    description=models.TextField(max_length=200, blank=True)
    sub_category_image=models.ImageField(upload_to='photos/subcategory', blank=True)
    subcategory_offer=models.FloatField(default=0, null=True, blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name='SubCategory'
        verbose_name_plural='SubCategories'

    def get_url(self):
        return reverse('product-by-sub-category', args=[self.category.slug,self.slug])
    
    def __str__(self):
        return self.slug