from django.contrib import admin
from django.urls import path, include

from .views import MosquitoImagesViewSet

urlpatterns = [
    path("mosquito/create", MosquitoImagesViewSet.as_view({"post": "create"})),

]
