from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,Variation
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse
# Create your views here.
def _cart_id(request):#we are getting session key
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request,product_id):#since we are going to add product inside the cart we are going to write product_id from products in store app
    product = Product.objects.get(id=product_id)#get the product
    product_variation=[]
    if request.method == 'POST':
        for item in request.POST:
            key=item
            value=request.POST[key]
            try:
                variation =Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))#get the cart using cart_id present in the session,to store sessionkey in database to get that we are adding another function
    except Cart.DoesNotExist:
        cart=Cart.objects.create(  #for creating a new cartid
             cart_id=_cart_id(request)
        )
    cart.save()
        #assume that there is a product and cart, we have to put product inside cart the product becomes a cart item
        #in one cart there will be multiple products,so that we combine product and cart so that we get the cart_item
#we have to group the cart items to increase the cart quantity of a  item if we select same color and size again and again, instead of adding cart item everytime
## IDEA:
# we have to check if the variations we are adding to cart it is already present in cart are not if it exists we are going to increase quantity of a item,if it not exists we are going to create a new cart item
    is_cart_item_exists=CartItem.objects.filter(product=product,cart=cart).exists()#going to check if it is true ar false
    if is_cart_item_exists:
        # cart_item=CartItem.objects.get(product=product,cart=cart)#we get the product and cart
        cart_item=CartItem.objects.filter(product=product,cart=cart)#it will return cart_item objects
        # cart_item=CartItem.objects.create(product=product,quantity=1,cart=cart)#everytime we are creating cart item with different color and size
        #existing_variations-->database
        #current_variations--->product_variation
        #item_id--->database
        ex_var_list=[]
        id=[]
        for item in cart_item:
            existing_variations=item.variations.all()#to get all items in cart_item object,we have to make list of variations because we have multiple variations with color and size
            ex_var_list.append(list(existing_variations))
            id.append(item.id)
        print(ex_var_list)
        if product_variation in ex_var_list:
            #increase the cart item quantity of course we need a cart_id
            index=ex_var_list.index(product_variation)#index function is same as len finding
            item_id=id[index]
            item = CartItem.objects.get(product=product,id=item_id)
            item.quantity += 1
            item.save()
        else:
#to select varition list in to database
            item=CartItem.objects.create(product=product,quantity=1,cart=cart)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            # cart_item.quantity +=1
            item.save()

    else:
        cart_item=CartItem.objects.create(  #for creating a new cartitem
                product=product,
                quantity=1,
                cart=cart
        )
        #to select varition list in to database
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')
def remove_cart(request,product_id,cart_item_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    try:
        cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if  cart_item.quantity > 1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request,product_id,cart_item_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request,total=0,quantity=0,cart_items=None):
    try:
        tax=0
        grand_total=0
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total +=(cart_item.product.price*cart_item.quantity)
            quantity +=cart_item.quantity
        tax=(2*total)/100
        grand_total=total+tax
    except ObjectDoesNotExist:
        pass


    context ={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,

    }
    return render(request,'store/cart.html',context)
