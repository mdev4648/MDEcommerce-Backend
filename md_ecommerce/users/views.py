from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .serializers import RegisterSerializer
from .serializers import ProfileSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .models import PasswordResetOTP,User
import random
from django.core.mail import EmailMessage
from django.db import transaction


class RegisterView(generics.CreateAPIView):#DRF view class that handles POST for creating objects
    serializer_class = RegisterSerializer #tells Django which serializer to use
    permission_classes = [AllowAny]

class ProfileView(APIView): #APIView → generic DRF class for handling HTTP methods
    permission_classes = [IsAuthenticated]

    def get(self, request): #handles GET requests
        user = request.user#automatically attached by JWT authentication
        serializer = ProfileSerializer(user)#Convert model to JSON
        return Response(serializer.data)#send JSON back to client


class RequestPasswordResetOTPView(APIView):

    def post(self, request):
        email_address = request.data.get("email")

        try:
            user = User.objects.get(email=email_address)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        otp = str(random.randint(100000, 999999))

        PasswordResetOTP.objects.create(user=user, otp=otp)
        email = EmailMessage(
            subject=f"Password Reset OTP",
            body=f"""
                    <p>Please verify your identity with this OTP:</p>
                    <h2 style="color:#2E86C1;"><b>{otp}</b></h2>
                   """,
            to=[email_address],
        )
        email.content_subtype = "html"  # This makes it HTML
        email.send()

        return Response({"message": "OTP sent to email"})


class VerifyOTPView(APIView):

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        try:
            user = User.objects.get(email=email)
            otp_record = PasswordResetOTP.objects.filter(
                user=user, otp=otp, is_verified=False
            ).latest("created_at")

        except:
            return Response({"error": "Invalid OTP"}, status=400)

        if otp_record.is_expired():
            return Response({"error": "OTP expired"}, status=400)

        otp_record.is_verified = True
        otp_record.save()

        return Response({"message": "OTP verified"})


class ResetPasswordView(APIView):

    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")

        try:
            user = User.objects.get(email=email)
            otp_record = PasswordResetOTP.objects.filter(
                user=user, is_verified=True, status="ACTIVE"
            ).latest("created_at")

        except:
            return Response({"error": "OTP not verified OR Active"}, status=400)

        with transaction.atomic():
            user.set_password(new_password)
            user.save()
            otp_record.status="VERIFIED"
            otp_record.save()

        return Response({"message": "Password reset successful"})