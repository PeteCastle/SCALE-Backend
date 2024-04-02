from django.shortcuts import render
from .serializers import MosquitoImagesSerializer, SystemSerializer, ImageSerializer, AreaCoverageSerializer
from .models import Images, System, AreaCoverage, SystemFumigation, SystemWaterLevel

from django.db.models import Sum, Count, Max
from django.db.models.functions import TruncDate, TruncMinute


from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .pagination import CustomPagination
import base64
from django.utils import timezone


from django.db.models.functions import ExtractMonth, ExtractYear

from datetime import timedelta



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
    
class DashboardFumigationViewSet(viewsets.ModelViewSet):
    queryset = SystemFumigation.objects.all()

    def count_by_date(self, request, *args, **kwargs):

        system_ids = request.query_params.get('system', None)
        month_date = request.query_params.get('date', None)

        data = System.objects.annotate(
            fumigation_date=TruncDate('systemfumigation__fumigation_date')
        ).values('id', 'name', 'fumigation_date').annotate(
            count=Count('systemfumigation')
        ).order_by('-fumigation_date')

        if system_ids:
            print("System ids", system_ids)
            data = data.filter(id__in=system_ids.split(','))
        
        if month_date:
            print("Month date", month_date)
            dt_list = month_date.split('-')
            month_date = int(dt_list[1])
            month_year = int(dt_list[0])
            data = data.filter(fumigation_date__year=month_year, fumigation_date__month=month_date)
        else:
            current_year = timezone.now().year
            current_month = timezone.now().month
            data = data.filter(fumigation_date__year=current_year, fumigation_date__month=current_month)


        print(data.query)
        response = {}
        for d in data:
            try:
                response[str(d['fumigation_date'])][d['name']] = d['count']
            except KeyError:
                response[str(d['fumigation_date'])] = {}
                response[str(d['fumigation_date'])][d['name']] = d['count']

        return Response(response)


    def count_by_system(self, request, *args, **kwargs):
        system_ids = request.query_params.get('system', None)
        month_date = request.query_params.get('date', None)

        data = System.objects.annotate(
            count=Count('systemfumigation'),
            fumigation_date=TruncDate('systemfumigation__fumigation_date')
        ).values('id', 'name', 'count')

        if system_ids:
            print("System ids", system_ids)
            data = data.filter(id__in=system_ids.split(','))
        
        if month_date:
            print("Month date", month_date)
            dt_list = month_date.split('-')
            month_date = int(dt_list[1])
            month_year = int(dt_list[0])
            data = data.filter(fumigation_date__year=month_year, fumigation_date__month=month_date)
        else:
            current_year = timezone.now().year
            current_month = timezone.now().month
            data = data.filter(fumigation_date__year=current_year, fumigation_date__month=current_month)

        response = {}
        for d in data:
            response[d['name']] = d['count']
  
        return Response(response)


    def count_filtered_month(self, request, *args, **kwargs):
        month_date = request.query_params.get('date', None)

        current_year = timezone.now().year
        current_month = timezone.now().month

        data = SystemFumigation.objects \
        .annotate(month=ExtractMonth('fumigation_date')) \
        .annotate(year=ExtractYear('fumigation_date')) \
        .values('month', 'year') \
        .annotate(count=Count('*')) \
        .order_by('year', 'month') \
        .filter(year=current_year, month=current_month)

        return Response(
            {"count":data[0]['count']}
            )

class DashboardDetectionsViewset(viewsets.ModelViewSet):
    def history(self, request, *args, **kwargs):
        now = timezone.now()

        # Subtract an hour from the current time
        hour_ago = now - timedelta(hours=1)

        data = Images.objects.filter(date_uploaded__gte=hour_ago, date_uploaded__lte=now).annotate(
            minute=TruncMinute('date_uploaded')
        ).values('minute','system__name').annotate(count=Sum('detected_mosquito_count')).order_by('minute')
        
        response = {}
        for d in data:
            time = d['minute'].strftime('%H:%M:%S %p')

            try:
                response[time][d['system__name']] = d['count']
            except KeyError:
                response[time] = {}
                response[time][d['system__name']] = d['count']

        for key, value in response.items():
            response[key]["__all__"] = sum(value.values())
        return Response(response)
        
    def latest(self, request, *args, **kwargs):
        now = timezone.now()
        minute_ago = now - timedelta(minutes=1)

        data = Images.objects.filter(date_uploaded__gte=minute_ago).annotate(
            minute=TruncMinute('date_uploaded')
        ).values('minute','system__name').annotate(count=Sum('detected_mosquito_count')).order_by('minute')
        
        response = {}
        for d in data:
            time = d['minute'].strftime('%H:%M:%S %p')

            try:
                response[time][d['system__name']] = d['count']
            except KeyError:
                response[time] = {}
                response[time][d['system__name']] = d['count']

        for key, value in response.items():
            response[key]["__all__"] = sum(value.values())
        return Response(response)
   
    def count(self, request, *args, **kwargs):
        month_date = request.query_params.get('date', None)

        if month_date:
            print("Month date", month_date)
            dt_list = month_date.split('-')
            month_date = int(dt_list[1])
            month_year = int(dt_list[0])
            data = Images.objects.filter(date_uploaded__year=month_year, date_uploaded__month=month_date)
        else:
            current_year = timezone.now().year
            current_month = timezone.now().month
            data = Images.objects.filter(date_uploaded__year=current_year, date_uploaded__month=current_month)

        data = data.aggregate(total=Sum('detected_mosquito_count'))

        return Response(data)
    
class DashboardWaterLevelViewSet(viewsets.ModelViewSet):
    def retrieve(self, request, *args, **kwargs):
        data = SystemWaterLevel.objects.values('system__name', 'last_updated', 'water_level').order_by('system__name','-last_updated')

        response = {}
        for d in data:
            if d['system__name'] not in response.keys():
                response[d['system__name']] = d['water_level']
            else:
                continue
    
        return Response(response)

class DashboardKPIViewSet(viewsets.ModelViewSet):
    def retrieve(self, request, *args, **kwargs):
        return Response(
            {
            "average_inference_time":69420,
            "average_confidence":0.89,
            "precision_score": 0.90,
            "recall_score": 0.90,

        }
        )