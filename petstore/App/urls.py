
from django.urls import path


from . import views

# from App.models import Order



urlpatterns=[
    path('', views.register),
    path('product',views.product),
    path('register',views.register,name='register'),
    path('login',views.user_login,name='login'),
    path('logout',views.user_logout),
    path('catfilter/<cv>',views.catfilter),
    path('sort/<sv>',views.sortbyprice),
    path('pricefilter',views.pricefilter),
    path('search',views.search),
    path('productdetail/<pid>',views.productdetail),
    path('addtocart/<pid>',views.addtocart),
    path('viewcart',views.viewcart),
    path('updateqty/<x>/<cid>',views.updateqty),
    path('remove/<cid>',views.remove),
    path('placeorder',views.placeorder),
    path('fetchorder',views.fetchorder),
    path('makepayment',views.makepayment),
    path('paymentsuccess',views.paymentsuccess),
    path('landing',views.landing),
    path('orderhistory',views.orderhistory),
    # path('Order',views.Order),
]


