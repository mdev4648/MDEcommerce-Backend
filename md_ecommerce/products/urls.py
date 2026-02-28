from django.urls import path
from .views import ProductCreateView, ProductListView, ProductDetailView,AddToWishlistView,RemoveFromWishlistView,WishlistListView,AddProductRatingView

urlpatterns = [
    path('create/', ProductCreateView.as_view()),
    path('', ProductListView.as_view()),
    path('<int:pk>/', ProductDetailView.as_view()),
    path("wishlist/", WishlistListView.as_view()),
    path("wishlist/add/<int:product_id>/", AddToWishlistView.as_view()),
    path("wishlist/remove/<int:product_id>/", RemoveFromWishlistView.as_view()),
    path("rate/<int:product_id>/", AddProductRatingView.as_view()),
]