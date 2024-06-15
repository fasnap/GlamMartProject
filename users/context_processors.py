from . models import WishList

def counter(request):
    wishlist_count=0
    if 'admin' in request.path:
        return {}
    else:
        user=request.user
        if user.is_authenticated:
            wishlist_items=WishList.objects.filter(user=request.user)
            for item in wishlist_items:
                wishlist_count+=1
    return dict(wishlist_count=wishlist_count)