# Create your models here.
from django.db import models
from users.models import User
from django.conf import settings

class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)  
    created_at = models.DateTimeField(auto_now_add=True)
    @property #@property allows you to use a method like a normal field.
    def average_rating(self):
        ratings = self.ratings.all() #will return all ratings for that product.
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 1)
        return 0

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.URLField()  # store Cloudinary URL

    def __str__(self):
        return f"Image for {self.product.name}"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} - {self.product.name}"


class ProductRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="ratings")
    rating = models.IntegerField()  # 1 to 5
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.product.name} - {self.rating}"