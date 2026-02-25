from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .serializers import RegisterSerializer
from .serializers import ProfileSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class RegisterView(generics.CreateAPIView):#DRF view class that handles POST for creating objects
    serializer_class = RegisterSerializer #tells Django which serializer to use
    permission_classes = [AllowAny]

class ProfileView(APIView): #APIView → generic DRF class for handling HTTP methods
    permission_classes = [IsAuthenticated]

    def get(self, request): #handles GET requests
        user = request.user#automatically attached by JWT authentication
        serializer = ProfileSerializer(user)#Convert model to JSON
        return Response(serializer.data)#send JSON back to client