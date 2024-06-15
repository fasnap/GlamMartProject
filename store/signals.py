from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from category.models import Category, SubCategory
from . models import Product

def calculate_final_offer(product):
    category_offer=product.category.category_offer if product.category.category_offer else 0
    subcategory_offer=product.sub_category.subcategory_offer if product.sub_category.subcategory_offer else 0
    product_offer=product.product_offer if product.product_offer else 0

    final_offer=max(category_offer,subcategory_offer,product_offer)
    return final_offer

@receiver(pre_save, sender=Product)
def set_product_offer(sender, instance, **kwargs):
    instance.offer=calculate_final_offer(instance)
    instance.offer_price=instance.actual_price - (instance.actual_price * (instance.offer / 100))

@receiver(post_save, sender=Category)
def update_products_on_category_offer_change(sender, instance, **kwargs):
    products=Product.objects.filter(category=instance)
    for product in products:
        product.save()

@receiver(post_save, sender=SubCategory)
def update_products_on_subcategory_offer_change(sender, instance, **kwargs):
    products=Product.objects.filter(sub_category=instance)
    for product in products:
        product.save()