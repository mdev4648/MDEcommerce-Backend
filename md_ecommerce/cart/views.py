from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))

        cart, created = Cart.objects.get_or_create(user=user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id
        )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        return Response({"message": "Product added to cart"}, status=status.HTTP_200_OK)



#Mulitple in one Request

    # def post(self, request):
    #     user = request.user
    #     items = request.data.get("items", [])

    #     cart, created = Cart.objects.get_or_create(user=user)

    #     for item in items:
    #         product_id = item.get("product")
    #         quantity = int(item.get("quantity", 1))

    #         cart_item, created = CartItem.objects.get_or_create(
    #             cart=cart,
    #             product_id=product_id
    #         )

    #         if not created:
    #             cart_item.quantity += quantity
    #         else:
    #             cart_item.quantity = quantity

    #         cart_item.save()

    #     return Response({"message": "Items added to cart"})


        

class ViewCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)