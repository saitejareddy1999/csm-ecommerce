from django.shortcuts import render,get_object_or_404
from .models import Product
from categories.models import Category
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
# Create your views here.
def store(request,category_slug=None):
    categories=None
    products=None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        product_count=products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        product_count=products.count()
#pagination starting
    # paginator=Paginator(products,5)
    # page_number=request.GET.get('page')
    # try:
    #     products=paginator.page(page_number)
    # except PageNotAnInteger:
    #     products=paginator.page(1)
    # except EmptyPage:
    #     products=paginator.page(paginator.num_pages)
    context = {
        'products':products,
        'product_count':product_count,
    }
    return render(request,'store/store.html',context)
def product_detail(request,category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
    except exception as e:
        raise e
    context ={
    'single_product':single_product
    }
    return render(request,'store/product_detail.html',context)
