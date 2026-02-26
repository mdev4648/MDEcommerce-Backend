from django.urls import path
from .views import CreateOrderView,ViewOrderView,OrderDetailView,CancelOrderView,AdminUpdateOrderStatusView

urlpatterns = [
    path("create/", CreateOrderView.as_view()),
    path("view/", ViewOrderView.as_view()),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:pk>/cancel/", CancelOrderView.as_view(), name="cancel-order"),
    path("admin/orders/<int:pk>/update-status/", AdminUpdateOrderStatusView.as_view(), name="admin-update-order-status"),
]