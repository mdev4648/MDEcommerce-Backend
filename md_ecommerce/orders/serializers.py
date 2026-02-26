from rest_framework import serializers
from .models import Order, OrderItem,ShippingAddress


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "price", "quantity", "total_price"]

    def get_total_price(self, obj):
        return obj.get_total_price()

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = "__all__"
        read_only_fields = ["user", "order"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source="user.email")
    shipping_address = ShippingAddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "items", "total_price", "status", "created_at", "shipping_address"]


