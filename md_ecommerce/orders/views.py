from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from cart.models import Cart
from .models import Order, OrderItem,ShippingAddress
from .serializers import OrderSerializer
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAdminUser




class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total_price = cart.get_cart_total()

        order = Order.objects.create(
            user=request.user,
            total_price=total_price
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,  # snapshot
                quantity=item.quantity
            )

        ShippingAddress.objects.create(
            user=request.user,
            order=order,
            full_name=request.data.get("full_name"),
            email=request.data.get("email"),
            phone=request.data.get("phone"),
            address=request.data.get("address"),
            city=request.data.get("city"),
            postal_code=request.data.get("postal_code"),
            country=request.data.get("country"),
            )
        cart_items.delete()  # clear cart after order

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

        
class ViewOrderView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

    # def get(self, request):
    #     order = Order.objects.get(user=request.user)
    #     serializer = OrderSerializer(order)
    #     return Response(serializer.data)



class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_object(self):
        order = super().get_object()
        if order.user != self.request.user:
            raise PermissionDenied("You do not have permission to view this order.")
        return order

class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        if order.status in ["SHIPPED", "DELIVERED"]:
            return Response(
                {"error": "Cannot cancel shipped or delivered orders"},
                status=400
            )

        order.status = "CANCELLED"
        order.save()

        return Response({"message": "Order cancelled successfully"})

class AdminUpdateOrderStatusView(UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "pk"
