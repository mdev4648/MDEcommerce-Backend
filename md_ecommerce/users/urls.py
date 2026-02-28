from django.urls import path
from .views import RegisterView, ProfileView,RequestPasswordResetOTPView,VerifyOTPView,ResetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path("password/request-otp/", RequestPasswordResetOTPView.as_view()),
    path("password/verify-otp/", VerifyOTPView.as_view()),
    path("password/reset/", ResetPasswordView.as_view()),
]