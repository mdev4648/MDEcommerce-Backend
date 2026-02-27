from rest_framework import serializers
from .models import Order, OrderItem,ShippingAddress,Payment
from cart.models import Cart


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


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["payment_method", "payment_status", "transaction_id", "paid_at"]
        read_only_fields = ["payment_status", "transaction_id", "paid_at"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source="user.email")
    shipping_address = ShippingAddressSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "items", "total_price", "status", "created_at", "shipping_address","payment"]


class CheckoutSummarySerializer(serializers.Serializer):
    items = serializers.SerializerMethodField()
    cart_total = serializers.SerializerMethodField()
    available_payment_methods = serializers.SerializerMethodField()

    def get_items(self, obj):
        cart = obj
        return [
            {
                "product_id": item.product.id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": item.product.price,
                "total_price": item.product.price * item.quantity
            }
            for item in cart.items.all()
        ]

    def get_cart_total(self, obj):
        return obj.get_cart_total()

    def get_available_payment_methods(self, obj):
        return ["COD", "CHAPA"]