from django.urls import path
from .views import CreateOrderView,ViewOrderView,OrderDetailView,CancelOrderView,AdminUpdateOrderStatusView,AdminMarkCODPaidView,CheckoutSummaryView,InitializeChapaPaymentView,VerifyChapaPaymentView
from.utils import send_invoice_email

urlpatterns = [
    path("create/", CreateOrderView.as_view()),
    path("view/", ViewOrderView.as_view()),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:pk>/cancel/", CancelOrderView.as_view(), name="cancel-order"),
    path("admin/orders/<int:pk>/update-status/", AdminUpdateOrderStatusView.as_view(), name="admin-update-order-status"),
    path("admin/orders/<int:pk>/mark-cod-paid/",AdminMarkCODPaidView.as_view(),name="admin-mark-cod-paid"),
    path("checkout-summary/", CheckoutSummaryView.as_view(), name="checkout-summary"),
    path("chapa/initialize/<int:order_id>/", InitializeChapaPaymentView.as_view()),
    path("verify-chapa/", VerifyChapaPaymentView.as_view()),
    # path("send-invoice/<int:order_id>/", SendInvoiceView.as_view()),
]