from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product, contactenquiry, Cart, Order, Orderhistory

# from App.models import Order


# Register your models here.
#admin.site.register(product)

class ProductAdmin(admin.ModelAdmin):
    list_display=['id','name','age','cat','pdetail','is_active']
    list_filter=['cat','is_active']
admin.site.register(Product,ProductAdmin)

class ContactenquiryAdmin(admin.ModelAdmin):
    class Meta:
        model=contactenquiry
    list_display=['name','email','message']

admin.site.register(contactenquiry,ContactenquiryAdmin)

admin.site.register((Cart,Order))

admin.site.register(Orderhistory)