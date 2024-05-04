from django.shortcuts import render
from .serializers import MosquitoImagesSerializer, SystemSerializer, ImageSerializer, AreaCoverageSerializer, WaterLevelSerializer, AreaListSerializer
from .models import Images, System, AreaCoverage, SystemFumigation, SystemWaterLevel, SystemStatus

from django.db.models import Sum, Count, Max
from django.db.models.functions import TruncDate, TruncMinute, TruncWeek, TruncMonth, TruncHour


from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .pagination import CustomPagination
import base64
from django.utils import timezone


from django.db.models.functions import ExtractMonth, ExtractYear, ExtractWeek

from datetime import timedelta, datetime
from django.core.files.base import ContentFile
from dateutil.relativedelta import relativedelta
import random

# Create your views here.
class MosquitoImagesViewSet(viewsets.ModelViewSet):
    queryset = Images.objects.all()
    serializer_class = MosquitoImagesSerializer

    def create(self, request, *args, **kwargs):
        image_data = base64.b64decode(request.data['image'])
        secret_key = request.data['secret_key']

        image_file = ContentFile(image_data, 'temp.jpg')

        payload = {
            'photo': image_file,
            'secret_key': secret_key,
        }

    
        serializer = self.get_serializer(data=payload)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            SystemStatus.objects.create(
                system_id=serializer.validated_data['system_id'],
                status=True
            )
            self.perform_create(serializer)
     
        # headers = self.get_success_headers(serializer.data)

        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(status=status.HTTP_201_CREATED)

class WaterLevelViewSet(viewsets.ModelViewSet):
    serializer_class  = WaterLevelSerializer
    def create(self, request, *args, **kwargs):
        # secret_key = request.data['secret_key']
        # water_level = request.data['water_level']

        # payload = {
        #     'secret_key': secret_key,
        #     'water_level': water_level
        # }
   
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else: 
            self.perform_create(serializer)

        return Response({"message": "Water level updated"}, status=status.HTTP_201_CREATED)


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
    
    def should_fumigate(self, request, system_id=None, *args, **kwargs):
        return Response(random.randint(0, 1), status=status.HTTP_200_OK)


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
    
    def list(self, request, *args, **kwargs):
        serializer = AreaListSerializer(self.queryset, many=True)
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

        response = {}
        for d in data:
            try:
                response[str(d['fumigation_date'])][d['name']] = d['count']
            except KeyError:
                response[str(d['fumigation_date'])] = {}
                response[str(d['fumigation_date'])][d['name']] = d['count']

        return Response(response)
    
    def count_by_week(self, request, *args, **kwargs):
        system_ids = request.query_params.get('system', None)
        month_date = request.query_params.get('date', None)

        data = System.objects.annotate(
            fumigation_date=TruncWeek('systemfumigation__fumigation_date'),
            
        ).values('fumigation_date').annotate(
            count=Count('systemfumigation'),
            week_number=ExtractWeek('fumigation_date')
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

        response = {}
        for _, d in enumerate(data):
            
            response[f"Week {d['week_number']}"] = d['count']
      
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

        current_date = timezone.now()
        current_year = current_date.year
        current_month = current_date.month

        # Calculate previous month and year
        prev_date = current_date - relativedelta(months=1)
        prev_year = prev_date.year
        prev_month = prev_date.month

        data = SystemFumigation.objects \
        .annotate(month=ExtractMonth('fumigation_date')) \
        .annotate(year=ExtractYear('fumigation_date')) \
        .values('month', 'year') \
        .annotate(count=Count('*')) \
        .order_by('year', 'month')

        # Filter for current month
        current_month_data = data.filter(year=current_year, month=current_month)

        # Filter for previous month
        prev_month_data = data.filter(year=prev_year, month=prev_month)

        current_count = current_month_data[0]['count'] if current_month_data else 0
        prev_month_count = prev_month_data[0]['count'] if prev_month_data else 0


        if prev_month_count != 0:
            change = ((current_count - prev_month_count) / prev_month_count) * 100
        else:
            change = 0 if current_count == 0 else 100

        return Response(
            {
                "count": current_count,
                "prev_month_count": prev_month_count,
                "change": change
            }
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
            dt_list = month_date.split('-')
            month_date = int(dt_list[1])
            month_year = int(dt_list[0])
            current_date = datetime(month_year, month_date, 1).date()
            data = Images.objects.filter(date_uploaded__year=month_year, date_uploaded__month=month_date)
        else:
            current_date = timezone.now()
            current_year = current_date.year
            current_month = current_date.month
            data = Images.objects.filter(date_uploaded__year=current_year, date_uploaded__month=current_month)

        # Calculate previous month and year
        prev_date = current_date - relativedelta(months=1)
        prev_year = prev_date.year
        prev_month = prev_date.month

        # Filter for previous month
        prev_data = Images.objects.filter(date_uploaded__year=prev_year, date_uploaded__month=prev_month)

        current_count = data.aggregate(total=Sum('detected_mosquito_count'))['total'] or 0
        prev_month_count = prev_data.aggregate(total=Sum('detected_mosquito_count'))['total'] or 0

        # Calculate percentage change
        if prev_month_count != 0:
            change = ((current_count - prev_month_count) / prev_month_count) * 100
        else:
            change = 0 if current_count == 0 else 100

        return Response(
            {
                "count": current_count,
                "prev_month_count": prev_month_count,
                "change": change
            }
        )
    
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

class DashboardUptimeViewSet(viewsets.ModelViewSet):
    def retrieve(self, request, *args, **kwargs):
        systems = request.query_params.get('system', None)
        by = request.query_params.get('by', 'day')
        limit = int(request.query_params.get('limit', 10))

        if systems:
            systems = [int(x) for x in systems.split(',')]
            data = SystemStatus.objects.filter(system_id__in=systems, status=True,)
        else:
            data = SystemStatus.objects.filter(status=True)

        if by == 'hour':
            dt_str = "%H:%M:%S"
            uptime_div = 60
            data = data.annotate(date=TruncHour('last_updated')).values('date').annotate(count=Count('date')).order_by('date')[:limit]
        elif by == 'day':
            dt_str = "%Y-%m-%d"
            uptime_div = 3600
            data = data.annotate(date=TruncDate('last_updated')).values('date').annotate(count=Count('date')).order_by('date')[:limit]
        elif by == 'week':
            dt_str = "%Y-%m-%d"
            uptime_div = 25200
            data = data.annotate(date=TruncWeek('last_updated')).values('date').annotate(count=Count('date')).order_by('date')[:limit]
        elif by == 'month':
            dt_str = "%Y-%m"
            uptime_div = 25200
            data = data.annotate(date=TruncMonth('last_updated')).values('date').annotate(count=Count('date')).order_by('date')[:limit]
        else:
            raise Response(f"Invalid value 'by'", status=400)

        response = {}
        for d in data:
            time = d['date'].strftime(dt_str)

            uptime = int((d['count'] / uptime_div) * 100)
            uptime = uptime if uptime < 100 else 100
            response[time] = uptime

        return Response(response)