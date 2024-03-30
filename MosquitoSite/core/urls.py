from django.contrib import admin
from django.urls import path, include

from .views import MosquitoImagesViewSet, SystemViewSet, ImageViewSet, CoverageViewSet

urlpatterns = [
    path("mosquito/create", MosquitoImagesViewSet.as_view({"post": "create"})),
    path("v1/system/details", SystemViewSet.as_view({"get": "system_details"})),
    path("v1/system/list", SystemViewSet.as_view({"get": "system_list"})),
    path("v1/system/<int:system_id>/status", SystemViewSet.as_view({"get": "status"})),
    
    path("v1/system/<int:system_id>/captures/recent", ImageViewSet.as_view({"get": "recent"})),
    path("v1/system/<int:system_id>/captures/history", ImageViewSet.as_view({"get": "history"})),
    path("v1/coverage/<int:area_id>", CoverageViewSet.as_view({"get": "retrieve"}, name="coverage")),

]
