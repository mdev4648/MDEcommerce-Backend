from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    # profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    profile_image = models.URLField(blank=True, null=True)  # Store Cloudinary URL  and URLField will store the image URL returned by Cloudinary after upload.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email