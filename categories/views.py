from django.shortcuts import render
from store.models import Product
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
# Create your views here.
def home(request):
    products = Product.objects.all().filter(is_available=True)
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
    }
    return render(request, 'pages/home.html',context)
