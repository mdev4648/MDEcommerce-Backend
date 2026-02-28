from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    # profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    profile_image = models.URLField(blank=True, null=True)  # Store Cloudinary URL  and URLField will store the image URL returned by Cloudinary after upload.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class PasswordResetOTP(models.Model):
    OTP_STATUS = [
        ("ACTIVE", "Active"),
        ("VERIFIED", "Verified"),        
        ("EXPIRED", "Expired"),
        
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    status = models.CharField(max_length=20, choices=OTP_STATUS, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.email} - {self.otp}"