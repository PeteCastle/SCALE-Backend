from django.shortcuts import render
from .serializers import MosquitoImagesSerializer, SystemSerializer, ImageSerializer, AreaCoverageSerializer
from .models import Images, System, AreaCoverage

from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .pagination import CustomPagination
import base64

# Create your views here.
class MosquitoImagesViewSet(viewsets.ModelViewSet):
    queryset = Images.objects.all()
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

class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer

    def system_list(self, request, *args, **kwargs):
        serializer = SystemSerializer(self.queryset, many=True)
        return Response(serializer.data)
    
    def system_details(self, request, *args, **kwargs):
        # system = self.get_object()
        serializer = SystemSerializer(self.queryset, detail=True, many=True)
        return Response(serializer.data)
    
    def status(self, request, system_id=None, *args, **kwargs):
        system = self.queryset.get(id = system_id)
        return Response({"message": system.latest_status})
    
class ImageViewSet(viewsets.ModelViewSet):
    queryset = Images.objects.all()
    serializer_class = ImageSerializer
    pagination_class = CustomPagination

    def recent(self, request, system_id = None,  *args, **kwargs):
        system = self.queryset.filter(system_id=system_id).last()
        serializer = ImageSerializer(system)
        return Response(serializer.data)
    
    def history(self, request, system_id = None,  *args, **kwargs):
        system = self.queryset.filter(system_id=system_id).order_by('-date_uploaded')
        page = self.paginate_queryset(system)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
class CoverageViewSet(viewsets.ModelViewSet):
    queryset = AreaCoverage.objects.all()
    serializer_class = AreaCoverageSerializer

    def retrieve(self, request, area_id = None, *args, **kwargs):
        area = self.queryset.get(id = area_id)
        serializer = AreaCoverageSerializer(area)
        return Response(serializer.data)
    

   