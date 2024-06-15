from . models import Category,SubCategory

def menu_links(request):
    categories_with_subcategories = []
    categories = Category.objects.all()
    
    for category in categories:
        subcategories = SubCategory.objects.filter(category=category)
        categories_with_subcategories.append({
            'category': category,
            'subcategories': subcategories
        })
    
    return {'categories_with_subcategories': categories_with_subcategories}