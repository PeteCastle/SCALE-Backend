from django.contrib import admin
from django.urls import path, include

from .views import (MosquitoImagesViewSet, 
                    SystemViewSet, 
                    ImageViewSet, 
                    CoverageViewSet, 
                    DashboardFumigationViewSet, 
                    DashboardDetectionsViewset, 
                    DashboardWaterLevelViewSet,
                    DashboardKPIViewSet,
                    DashboardUptimeViewSet)

urlpatterns = [
    path("v1/mosquito/create", MosquitoImagesViewSet.as_view({"post": "create"})),
    path("v1/system/details", SystemViewSet.as_view({"get": "system_details"})),
    path("v1/system/list", SystemViewSet.as_view({"get": "system_list"})),
    path("v1/system/<int:system_id>/status", SystemViewSet.as_view({"get": "status"})),
    
    path("v1/system/<int:system_id>/captures/recent", ImageViewSet.as_view({"get": "recent"})),
    path("v1/system/<int:system_id>/captures/history", ImageViewSet.as_view({"get": "history"})),
    path("v1/coverage/<int:area_id>", CoverageViewSet.as_view({"get": "retrieve"}, name="coverage")),

    path("v1/dashboard/fumigations/date", DashboardFumigationViewSet.as_view({"get": "count_by_date"})),
    path("v1/dashboard/fumigations/system", DashboardFumigationViewSet.as_view({"get": "count_by_system"})),
    path("v1/dashboard/fumigations/week", DashboardFumigationViewSet.as_view({"get": "count_by_week"})),
    path("v1/dashboard/fumigations/count", DashboardFumigationViewSet.as_view({"get": "count_filtered_month"})),

    path('v1/dashboard/detections/history', DashboardDetectionsViewset.as_view({"get": "history"})),
    path('v1/dashboard/detections/latest', DashboardDetectionsViewset.as_view({"get": "latest"})),
    path('v1/dashboard/detections/count', DashboardDetectionsViewset.as_view({"get": "count"})),

    path('v1/dashboard/water_level/status', DashboardWaterLevelViewSet.as_view({"get": "retrieve"})),

    path('v1/dashboard/kpi', DashboardKPIViewSet.as_view({"get": "retrieve"})),

    path('v1/dashboard/uptime', DashboardUptimeViewSet.as_view({"get": "retrieve"})),
]
