from django.shortcuts import render,redirect,get_object_or_404
from .forms import *
from accounts.models import UserProfile,Account

from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
# from .models import
from carts.views import _cart_id
from carts.models import Cart,CartItem
from orders.models import Order,OrderProduct
import requests


# Create your views here.
def register(request):
    if request.method == 'POST':
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username=email.split('@')[0]
            user=Account.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.phone_number =phone_number
            user.save()

            profile=UserProfile()
            profile.user_id=user.id
            profile.profile_picture='default/default-user.jpg'
            profile.save()
            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request,'successfully registered')
            # return redirect('register')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context ={
    'form':form
    }
    return render(request,'accounts/register.html',context)
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                print('try block')
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                print(is_cart_item_exists)
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # product_variation = [1, 2, 3, 4, 6]
                    # ex_var_list = [4, 6, 3, 5]

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                print('except block')
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                print(query)
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')
# def login(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#
#         user=auth.authenticate(email=email,password=password)
#         if user is not None:
#             try:
#                 print('try block')
#                 cart=Cart.objects.get(cart_id=_cart_id(request))#we are checking  anything is inside cart
#                 is_cart_item_exists=CartItem.objects.filter(cart=cart).exists()#we just assign the user to cartitem
#                 print(is_cart_item_exists)
#                 if is_cart_item_exists:
#                     cart_item=CartItem.objects.filter(cart=cart)#this line actually gives us which are the cart item present/assigned inside cart_id
#                      # Getting the product variations by cart id
#                     product_variation = []
#                     for item in cart_item:
#                         variation = item.variations.all()
#                         product_variation.append(list(variation))
#
#                     # Get the cart items from the user to access his product variations
#                     cart_item = CartItem.objects.filter(user=user)
#                     ex_var_list = []
#                     id = []
#                     for item in cart_item:
#                         existing_variation = item.variations.all()
#                         ex_var_list.append(list(existing_variation))
#                         id.append(item.id)
#
#                     # product_variation = [1, 2, 3, 4, 6]
#                     # ex_var_list = [4, 6, 3, 5]
#
#                     for pr in product_variation:
#                         if pr in ex_var_list:
#                             index = ex_var_list.index(pr)
#                             item_id = id[index]
#                             item = CartItem.objects.get(id=item_id)
#                             item.quantity += 1
#                             item.user = user
#                             item.save()
#                         else:
#                             cart_item = CartItem.objects.filter(cart=cart)
#                             for item in cart_item:
#                                 item.user = user
#                                 item.save()
#
#             except:
#                 pass
#             auth.login(request,user)
#             messages.success(request,'you are logged in')
#             url = request.META.get('HTTP_REFERER')
#             try:
#                 query = requests.utils.urlparse(url).query
#                 # next=/cart/checkout/
#                 params = dict(x.split('=') for x in query.split('&'))
#                 if 'next' in params:
#                     nextPage = params['next']
#                     return redirect(nextPage)
#             except:
#                 return redirect('dashboard')
#
#         else:
#             messages.error(request,'invalid credantials')
#             return redirect('login')
#
#     return render(request,'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'you are logged out')
    return redirect('logout')

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count=orders.count()
    userprofile=UserProfile.objects.get(user_id=request.user.id)
    context={
    'orders_count':orders_count,
    'userprofile':userprofile
    }
    return render(request,'accounts/dashboard.html',context)

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')

def reset_password_validation(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request,'please reset the password')
        return redirect('reset_password')
    else:
        messages.error(request,'the link has been expired')
        return redirect('login')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('store')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/reset_password.html')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.order_by('-created_at').filter(user=request.user,is_ordered=True)
    context={
    'orders':  orders,
    }
    return render(request,'accounts/my_orders.html',context)
@login_required(login_url='login')
def edit_profile(request):
    userprofile=get_object_or_404(UserProfile,user=request.user)
    if request.method == 'POST':
        print('entered if')
        user_form=UserForm(request.POST,instance=request.user)
        profile_form=UserProfileForm(request.POST,request.FILES,instance=userprofile)
        print(user_form,profile_form)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'your profile has been updated.')
            return redirect('edit_profile')
    else:
        print('entered else')
        user_form=UserForm(instance=request.user)
        profile_form=UserProfileForm(instance=userprofile)
    context={
    'user_form':user_form,
    'profile_form':profile_form,
    'userprofile':userprofile
    }
    return render(request,'accounts/edit_profile.html',context)
@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password=request.POST['current_password']
        new_password=request.POST['new_password']
        confirm_password=request.POST['confirm_password']
        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,'password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request,'please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request,'password does not match')
            return redirect('change_password')
    return render(request,'accounts/change_password.html')
@login_required(login_url='login')
def order_detail(request,order_id):
    order_details=OrderProduct.objects.filter(order__order_number=order_id)
    order=Order.objects.get(order_number=order_id)
    sub_total= 0
    for i in order_details:
        sub_total +=i.product_price*i.quantity
    context={
    'order_details':order_details,
    'order':order,
    'sub_total':sub_total
    }
    return render(request,'accounts/order_detail.html',context)
