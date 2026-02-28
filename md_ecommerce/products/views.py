from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Product,Wishlist,ProductRating
from .serializers import ProductSerializer,WishlistSerializer,ProductRatingSerializer
from rest_framework.views import APIView
class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
from rest_framework.response import Response

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class AddToWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            return Response({"message": "Already in wishlist"})

        return Response({"message": "Added to wishlist"})
class RemoveFromWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        try:
            wishlist_item = Wishlist.objects.get(
                user=request.user,
                product_id=product_id
            )
            wishlist_item.delete()
            return Response({"message": "Removed from wishlist"})
        except Wishlist.DoesNotExist:
            return Response({"error": "Not in wishlist"}, status=404)


class WishlistListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(items, many=True)
        return Response(serializer.data)



class AddProductRatingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        rating_value = request.data.get("rating")
        review = request.data.get("review", "")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        rating_obj, created = ProductRating.objects.update_or_create(
            user=request.user,
            product=product,
            defaults={"rating": rating_value, "review": review}
        )

        return Response({"message": "Rating submitted"})