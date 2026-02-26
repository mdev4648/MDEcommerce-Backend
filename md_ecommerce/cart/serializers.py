from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_price = serializers.ReadOnlyField(source="product.price")
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "product_price", "quantity","total_price"]
    def get_total_price(self, obj):
        return obj.get_total_price()

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total =serializers.SerializerMethodField()# The name of field must be cart_total because the method name is get_cart_total
    # if we want overide method name get_cart_total  use like this>> cart_total = serializers.SerializerMethodField(method_name='calculate_total')
    user = serializers.ReadOnlyField(source="user.email")
    class Meta:
        model = Cart
        fields = ["id", "items","cart_total","user"]
    def get_cart_total(self, obj): 

        return obj.get_cart_total()