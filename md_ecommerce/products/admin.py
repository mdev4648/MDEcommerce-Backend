from django.contrib import admin

# Register your models here.
from .models import Product,ProductImage,ProductRating

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductRating)
