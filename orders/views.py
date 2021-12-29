from django.shortcuts import render,redirect

from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order,Payment,OrderProduct
from carts.models import CartItem
from store.models import Product
from django.http import JsonResponse
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your views here.
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    #next step Move the products to order Product Table
    cart_items=CartItem.objects.filter(user=request.user)#we are filtering by current_user
    for item in cart_items:
        orderproduct=OrderProduct()#we are creating orderproduct object
        orderproduct.order_id=order.id#we are getting id from order in model.py
        orderproduct.payment=payment
        orderproduct.user_id=request.user.id
        orderproduct.product_id=item.product_id
        orderproduct.quantity=item.quantity
        orderproduct.product_price=item.product.price
        orderproduct.ordered=True
        orderproduct.save()
        #we will cart_item by item id from CartItem
        cart_item=CartItem.objects.get(id=item.id)#we are taking cart_item by we are accessing id by cartitemid ,because we want to take the variations of that particular cart items
        product_variations=cart_item.variations.all()#we want to take the cartitem by variations  by that id to get all variations
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variations)
        orderproduct.save()
        #Reduce the qunatity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    #clear cart
    CartItem.objects.filter(user=request.user).delete()
    #send recived email to customer order is recived
    mail_subject = 'Thanku for u r order'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order':order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
    #send order number and transaction id back to send data method via jsonResponse
    data={
        'order_number':order.order_number,
        'transID':payment.payment_id,
    }

    return JsonResponse(data)
def place_order(request,total=0,quantity=0,):
    current_user = request.user

    #if the cart_count is less than or equal to 0,then redirect it to store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    tax=0
    grand_total=0
    for cart_item in cart_items:
        total +=(cart_item.product.price*cart_item.quantity)
        quantity +=cart_item.quantity
    tax=(2*total)/100
    grand_total=total+tax
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():

            data=Order() #instance of a forms
            # store all billing information inside order table
            data.user = current_user
            data.first_name = form.cleaned_data['first_name'] # to store all user input in database
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            #generate  order_number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20211217
            order_number = current_date + str(data.id)#data.id ==>when we submit form primary key is going to fetch it will store in id
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)#is_ordered will get True if we get order the product
            context={
            'order':order,
            'cart_items':cart_items,
            'total':total,
            'tax':tax,
            'grand_total':grand_total

            }

            return render(request,'orders/payments.html',context)
    else:
        return redirect('checkout')
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        order_products = OrderProduct.objects.filter(order_id=order.id)
        sub_total=0
        for i in order_products:
            sub_total += i.product_price * i.quantity
        payment= Payment.objects.get(payment_id=transID)
        context={
        'order':order,
        'order_products':order_products,
        'order_number':order.order_number,
        'transID':payment,
        'payment':payment,
        'sub_total':sub_total,
        }
        print(order,order_products,order_number)
        return render(request,'orders/order_complete.html',context)
    except (Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('home')
