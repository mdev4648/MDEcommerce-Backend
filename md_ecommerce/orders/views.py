from django.shortcuts import render
import requests
# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from cart.models import Cart
from .models import Order, OrderItem,ShippingAddress,Payment
from .serializers import OrderSerializer,CheckoutSummarySerializer
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAdminUser
from django.db import transaction# why we import? 
from django.utils import timezone


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic #Without transaction → broken data  With transaction → everything rolls back automatically
    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        # 🔴 CHECK STOCK BEFORE CREATING ORDER
        for item in cart_items:
            if item.quantity > item.product.stock:
                return Response(
                    {"error": f"Not enough stock for {item.product.name}"},
                    status=400
                )

        # ✅ Create Order
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

            product=item.product

            # 🔥 STOCK DEDUCTION HERE
            product.stock -= item.quantity
            product.save()

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

        payment_method = request.data.get("payment_method")
        if payment_method not in ["COD", "CHAPA"]:
            return Response({"error": "Invalid payment method"}, status=400)
        payment = Payment.objects.create(
                order=order,
                payment_method=payment_method
            )
                # 🔥 CASH ON DELIVERY LOGIC
        if payment_method == "COD":
            order.status = "PROCESSING"   # ready to ship
            order.save()

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


class AdminMarkCODPaidView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        # Check if payment exists
        if not hasattr(order, "payment"):
            return Response({"error": "Payment record not found"}, status=400)

        payment = order.payment

        if payment.payment_method != "COD":
            return Response(
                {"error": "This endpoint is only for Cash On Delivery payments"},
                status=400
            )

        if payment.payment_status == "SUCCESS":
            return Response(
                {"error": "Payment already marked as paid"},
                status=400
            )

        # ✅ Mark as paid
        payment.payment_status = "SUCCESS"
        payment.paid_at = timezone.now()
        payment.save()

        # ✅ Update order status
        order.status = "DELIVERED"
        order.save()

        return Response({"message": "COD payment marked as SUCCESS"})


class CheckoutSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)

        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        serializer = CheckoutSummarySerializer(cart)
        return Response(serializer.data)


class InitializeChapaPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        if order.payment.payment_method != "CHAPA":
            return Response({"error": "This order is not CHAPA payment"}, status=400)

        chapa_secret = "CHASECK_TEST-ZqWtAemMl9THVGVKCvthuSUkJ8HF763k"

        url = "https://api.chapa.co/v1/transaction/initialize"

        tx_ref = f"order_{order.id}"

        payload = {
            "amount": str(order.total_price),
            "currency": "ETB",
            "email": request.user.email,
            "first_name": request.user.username,
            "last_name": request.user.username,
            "tx_ref": tx_ref,
            "return_url": "http://localhost:8000/api/orders/verify-chapa/",
        }

        headers = {
            "Authorization": f"Bearer {chapa_secret}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        print("chapa initialize response",data)

        # Save transaction reference
        order.payment.transaction_id = tx_ref
        order.payment.save()

        return Response(data)



class VerifyChapaPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tx_ref = request.query_params.get("tx_ref")

        if not tx_ref:
            return Response({"error": "tx_ref required"}, status=400)

        chapa_secret = "CHASECK_TEST-ZqWtAemMl9THVGVKCvthuSUkJ8HF763k"
        url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"

        headers = {
            "Authorization": f"Bearer {chapa_secret}"
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        if data.get("status") == "success":
            try:
                payment = Payment.objects.get(transaction_id=tx_ref)
                payment.payment_status = "SUCCESS"
                payment.save()

                order = payment.order
                order.status = "PROCESSING"
                order.save()

                return Response({"message": "Payment verified successfully"})
            except Payment.DoesNotExist:
                return Response({"error": "Payment not found"}, status=404)

        return Response({"error": "Payment not successful"})


class VerifyChapaPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tx_ref = request.query_params.get("tx_ref")

        if not tx_ref:
            return Response({"error": "tx_ref required"}, status=400)

        chapa_secret = "CHASECK_TEST-ZqWtAemMl9THVGVKCvthuSUkJ8HF763k"
        url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"

        headers = {
            "Authorization": f"Bearer {chapa_secret}"
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        print("chapa payment verify", data)

        if data.get("status") == "success":
            try:
                payment = Payment.objects.get(transaction_id=tx_ref)
                payment.payment_status = "SUCCESS"
                payment.save()

                order = payment.order
                order.status = "PROCESSING"
                order.save()

                return Response({"message": "Payment verified successfully"})
            except Payment.DoesNotExist:
                return Response({"error": "Payment not found"}, status=404)

        return Response({"error": "Payment not successful"})