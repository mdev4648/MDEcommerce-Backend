from django.contrib import admin

# Register your models here.
from .models import Product,ProductImage,ProductRating,ProductVariant,VariantAttributeValue,VariantAttribute

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductImage)
admin.site.register(ProductRating)
admin.site.register(VariantAttribute)
admin.site.register(VariantAttributeValue)
