from django.shortcuts import render
from store.models import Product,ReviewRating
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
# Create your views here.
def home(request):
    products = Product.objects.all().filter(is_available=True)
    # Get the reviews
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
#pagination starting
    paginator=Paginator(products,3)
    page_number=request.GET.get('page')
    try:
        products=paginator.page(page_number)
    except PageNotAnInteger:
        products=paginator.page(1)
    except EmptyPage:
        products=paginator.page(paginator.num_pages)
    context = {
        'products':products,
        'reviews':reviews,
    }
    return render(request, 'pages/home.html',context)
