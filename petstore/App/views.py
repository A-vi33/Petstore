from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
# Create your views here.
from django.contrib.auth.models import User
import razorpay
from .models import Product,contactenquiry,Cart,Orderhistory
from .models import Order
import random
from django.http import HttpResponse
# from App.models import Order


def product(request):
    p=Product.objects.filter(is_active=True)
    #print(p)
    context={}
    context['data']=p
    return render(request,'index.html',context)


def landing(request):
    if request.method=='POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        message=request.POST.get('message')
        se=contactenquiry(name=name,email=email,message=message)
        se.save()
    return render(request,'index.html')

def fetchorder(request):
    o=Order.objects.filter(uid=request.user.id) # order details of a user
    context={'data':o}
    sum=0
    for x in o:
        sum=sum+x.amt
    context['total']=sum
    context['n']=len(o)

    orders_to_delete=list(o)

    for order in orders_to_delete:
        Orderhistory.objects.create(order=order,payment_status='successful')

    return render(request,'placeorder.html',context)

def updateqty(request,x,cid):
    c=Cart.objects.filter(id=cid) # cart info of a specific user
    q=c[0].qty # available quantity
    #print(type(x))
    if x == "1":
        q=q+1
    elif q>1:
        q=q-1

    c.update(qty=q)
    return redirect('/viewcart')

def catfilter(request,cv):
    q1=Q(is_active=True) # total available prods.
    q2=Q(cat=cv) # avialable prods in each catg.
    p=Product.objects.filter(q1 & q2)
    context={}
    context['data']=p
    return render(request,'index.html',context)

def sortbyprice(request,sv):
    if sv=='1':
        p=Product.objects.order_by("-price")
    else:
        p=Product.objects.order_by('price')

    context={}
    context['data']=p
    return render(request,'index.html',context)


def remove(request,cid):
    c=Cart.objects.filter(id=cid) # the item that we want to eliminate
    c.delete()
    return redirect('/viewcart')

def user_login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        n = request.POST['input1']  # Username
        p = request.POST['input2']  # Password
        u = authenticate(request, username=n, password=p)  # Proper authentication
        if u is not None:
            login(request, u)
            return redirect('/product')
        else:
            context = {}
            context['errormsg'] = 'Invalid credentials!!'
            return render(request, 'login.html',context)

def user_logout(request):
    logout(request)
    return redirect('/login')

def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        context = {}
        n = request.POST['uname']
        p = request.POST['upass']
        cp = request.POST['upass']

        # Validate the inputs
        if n == '' or p == '' or cp == '':
            context['errormsg'] = 'Fields cannot be empty!!'
            return render(request, 'register.html', context)
        elif len(p) < 8:
            context['errormsg'] = 'Password must be 8 characters long..!!'
            return render(request, 'register.html', context)
        elif p != cp:
            context['errormsg'] = 'Password and confirm password should be the same..!!'
            return render(request, 'register.html', context)
        else:
            try:
                u = User.objects.create(username=n, email=n)
                u.set_password(p)
                u.save()
                context['Success'] = 'User created successfully!!!'

                # Redirect to the login page after successful registration
                return redirect('login')  # Make sure 'login' is correctly mapped in your URL patterns
            except Exception:
                context['errormsg'] = 'User already exists. Enter a different username.'
                return render(request, 'register.html',context)


def makepayment(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

    # Get the user's orders
    orders = Order.objects.filter(uid=request.user.id)
    total_amount = 0
    orderid = None

    # Sum up the total amount from the user's orders
    for order in orders:
        total_amount += order.amt
        if not orderid:  # If orderid is None, set it to the first order's orderid
            orderid = order.orderid

    if total_amount == 0:
        context = {'error': 'No orders to pay for.'}
        return render(request, 'pay.html', context)

    # Prepare data for Razorpay payment
    data = {
        "amount": total_amount * 100,  # Amount in paise (Razorpay expects the amount in the smallest currency unit)
        "currency": "INR",
        "receipt": str(orderid),  # Unique receipt (order ID in this case)
    }

    try:
        payment = client.order.create(data=data)
        context = {
            'payment': payment,
        }
        return render(request, 'pay.html', context)
    except razorpay.errors.RazorpayError as e:
        context = {
            'error': f"Error creating Razorpay payment: {str(e)}",
        }
        return render(request, 'pay.html',context)

def placeorder(request):
    c=Cart.objects.filter(uid=request.user.id) # order details of a particular user
    orderid=random.randrange(1000,9999)
    for x in c:
        amount=x.qty*x.pid.price
        o=Order.objects.create(orderid=orderid,pid=x.pid,uid=x.uid,qty=x.qty, amt=amount) # info of order created
        o.save()

        x.delete()
    return redirect('/fetchorder')

def pricefilter(request):
    min=request.GET['min']
    max=request.GET['max']
    #print(min)
    #print(max)
    q1=Q(price__gte=min) # price >= min
    q2=Q(price__lte=max) # price <= max ## min -- price -- max
    p=Product.objects.filter(q1 & q2)
    context={}
    context['data']=p
    return render(request,'index.html',context)

def productdetail(request,pid):
    p=Product.objects.filter(id=pid)
    context={}
    context['data']=p # product details
    return render(request,'product_detail.html',context)

def addtocart(request,pid):
    if request.user.is_authenticated:
        #uid=request.user.id
        context={}
        u=User.objects.filter(id=request.user.id) # u is holding user id
        p=Product.objects.filter(id=pid)  # product info.
        #check product is exists or not
        q1=Q(uid=u[0])
        q2=Q(pid=p[0])
        c=Cart.objects.filter(q1 & q2)
        n=len(c)
        context['data']=p
        if n == 1:
            context['errmsg'] = "Pet Already Exist"
            return render(request, 'product_detail.html', context)
        else:
            c = Cart.objects.create(uid=u[0], pid=p[0])
            c.save()
            context['msg'] = "Pet added successfully in the cart"
            return render(request, 'product_detail.html', context)
            # return HttpResponse("Product added in cart")

    else:
        return redirect('/login')


def viewcart(request):
    c = Cart.objects.filter(uid=request.user.id)  # cart info of a perticular user id
    # print(c)
    context = {}
    context['data'] = c
    sum = 0
    for x in c:
        sum = sum + x.pid.price

    context['total'] = sum
    context['n'] = len(c)
    return render(request, 'cart.html', context)


def search(request):
    query=request.GET['query']
    #print(query)
    pname=Product.objects.filter(name__icontains=query) # 0
    pcat=Product.objects.filter(cat__icontains=query) # 0
    pdetail=Product.objects.filter(pdetail__icontains=query) # 0

    allprod=pname.union(pcat,pdetail) # 0
    context={}

    if allprod.count()==0:
        context['errmsg']='Dog not FOUND'

    context['data']=allprod
    return render(request,'index.html',context)

def paymentsuccess(request):
    sub='It vedant genderal store'
    msg='Thanks form Buying....!!'
    frm='mohith202421@gmail.com'
    u=User.objects.filter(id=request.user.id)
    to=u[0].email
    send_mail(
        sub,
        msg,
        frm,
        [to]    ,
        fail_silently=False
    )
    return render(request,'paymentsuccess.html')


def orderhistory(request):
    orders= Orderhistory.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request,'orderhistory.html',context)