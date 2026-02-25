from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
import cloudinary.uploader

class RegisterSerializer(serializers.ModelSerializer): # it inherit from other class
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    profile_image = serializers.ImageField(required=False)  # Accept image

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'phone', 'profile_image')

    def validate(self, attrs): #attrs → dictionary of all input fields
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        profile_image = validated_data.pop('profile_image', None)
        user = User.objects.create(#creates a new row in the database using Django ORM.
            email=validated_data['email'],
            username=validated_data['username'],
            phone=validated_data.get('phone', '')
        )

        user.set_password(validated_data['password'])#hashes password (never store plain text!)

         # Upload to Cloudinary if image exists
        if profile_image:
            upload_result = cloudinary.uploader.upload(profile_image)
            print("This is Upload Result", upload_result)
            print("This is Upload Result", upload_result.get('secure_url'))
            user.profile_image = upload_result.get('secure_url')

       
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'phone', 'profile_image')