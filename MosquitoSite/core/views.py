from django.shortcuts import render
from .serializers import MosquitoImagesSerializer
from .models import MosquitoImages

from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
import base64

# Create your views here.
class MosquitoImagesViewSet(viewsets.ModelViewSet):
    queryset = MosquitoImages.objects.all()
    serializer_class = MosquitoImagesSerializer

    def create(self, request, *args, **kwargs):
        # print(request.data['image'])

        image_data = base64.b64decode(request.data['image'])

        # Save the image or perform necessary operations here
        # Example: save the image to a file
        with open('received_image.jpg', 'wb') as file:
            file.write(image_data)
        serializer = self.get_serializer(request.POST, request.FILES)
        # print(serializer)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # print(serializer.data)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        

    def perform_create(self, serializer):
        serializer.save()
