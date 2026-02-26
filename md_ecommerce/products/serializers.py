from rest_framework import serializers
from .models import Product, ProductImage
import cloudinary.uploader


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True
    )

    product_images = ProductImageSerializer(
        many=True,
        read_only=True,
        source='images'
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'images', 'product_images']

    def create(self, validated_data):
        images = validated_data.pop('images')
        user = self.context['request'].user

        product = Product.objects.create(
            seller=user,
            **validated_data
        )

        for image in images:
            upload_result = cloudinary.uploader.upload(image)
            ProductImage.objects.create(
                product=product,
                image=upload_result.get('secure_url')
            )

        return product