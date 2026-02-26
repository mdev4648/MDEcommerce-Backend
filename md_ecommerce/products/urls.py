from django.urls import path
from .views import ProductCreateView, ProductListView, ProductDetailView

urlpatterns = [
    path('create/', ProductCreateView.as_view()),
    path('', ProductListView.as_view()),
    path('<int:pk>/', ProductDetailView.as_view()),
]