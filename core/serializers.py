from rest_framework import serializers

from core.models import Images, System, Images, AreaCoverage, SystemWaterLevel
import time

from rcnn.predictor import predict
from datetime import datetime
from django.conf import settings
import boto3
from core.models import Detections

from django.core.files.base import ContentFile
 
class MosquitoImagesSerializer(serializers.ModelSerializer):
    # image_bmp = serializers.SerializerMethodField()
    secret_key = serializers.CharField(write_only=True)
    count = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(MosquitoImagesSerializer, self).__init__(*args, **kwargs)
        self.s3 = boto3.client('s3', 
                            region_name=settings.AWS_S3_REGION_NAME,
                            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                        )

    def get_count(self, obj):
        return obj.system.detections.count()

    class Meta:
        model = Images
        fields = [
            "photo",
            "secret_key",
            "count"
            # "image_bmp"
        ]
   
    def validate(self, fields):
        secret_key = fields.get("secret_key")

        system = System.objects.filter(secret_key=secret_key)

        if secret_key is None or system.count() == 0:
            raise serializers.ValidationError("Invalid secret key.")
        
        return {
            "photo": fields.get("photo"),
            "system": system.first(),
            "area": system.first().coverage,
        }
        print(fields)

    def create(self, validated_data):
        start_time = time.time()

        system = validated_data["system"]
        image = validated_data["photo"]
        file_name = f'temp/system_{system.id}_{datetime.now().isoformat()}.jpg'
        self.s3.upload_fileobj(image, 
                            settings.AWS_STORAGE_BUCKET_NAME,
                            file_name
                            )
        
        print(start_time - time.time())
        
        file_name, validated_data['detected_mosquito_count'], detections = predict.delay(file_name, validated_data["system"]).get()
        
        print(start_time - time.time())
        file_obj = self.s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_name)
        file_content = file_obj['Body'].read()
        print(start_time - time.time())

        for d in detections:
            Detections.objects.update_or_create(detection_id=id,system= d['detection_id'], defaults={
                    'x1': d['x1'],
                    'y1': d['y1'],
                    'x2': d['x2'],
                    'y2': d['y2'],
                    'score': d['scores'],
                    'detected_time': d['detected_time'],
            })

        print(start_time - time.time())
        validated_data['photo'] = ContentFile(file_content,f'system_{system.id}_{datetime.now().isoformat()}.jpg')
        print(validated_data['photo'])

        self.s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_name)
        print(start_time - time.time())
        
        end_time = time.time()
        validated_data['prediction_time'] = end_time - start_time

        print(validated_data['prediction_time'])
        return Images.objects.create(**validated_data)
    
class WaterLevelSerializer(serializers.ModelSerializer):
    secret_key = serializers.CharField(write_only=True)
    water_level = serializers.FloatField(max_value=100, min_value=0)

    class Meta:
        model = SystemWaterLevel
        fields = ["water_level","secret_key"]

    def validate(self, fields):
        secret_key = fields.get("secret_key")

        system = System.objects.filter(secret_key=secret_key)

        if secret_key is None or system.count() == 0:
            raise serializers.ValidationError("Invalid secret key.")
        
        return {
            "water_level": fields.get("water_level"),
            "system": system.first()
        }
    
    def create(self, validated_data):
        return SystemWaterLevel.objects.create(**validated_data)
        

class SystemSerializer(serializers.ModelSerializer):
    # secret_key = serializers.CharField(write_only=True)
    def __init__(self, *args, **kwargs):
        detail = kwargs.pop('detail', False)
        self.detail = detail
        super(SystemSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = System
        fields = "id", "name", "description", "image", "location_name", "location_latitude", "location_longitude", "location_radius","latest_status"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if self.detail:
            return {
                "id": data["id"],
                "name": data["name"],
                "description": data["description"],
                "image": data["image"],
                "location":{
                    "name": data["location_name"],
                    "latitude": data["location_latitude"],
                    "longitude": data["location_longitude"],
                    "radius": data["location_radius"],
                },
                "status": instance.latest_status,
  
            }
        else:
            return {
                "id": data["id"],
                "name": data["name"],
            }
        return data
    
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = "__all__"
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "time": data["date_uploaded"],
            "image": data["photo"],
            "location": instance.area.area_name,
            "count" : data["detected_mosquito_count"]
        }
    
class AreaCoverageSerializer(serializers.ModelSerializer):
    systems = SystemSerializer(many=True, detail=True)
    class Meta:
        model = AreaCoverage
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            "id": data["id"],
            "name": data["area_name"],
            "description": data["description"],
            "image": data["image"],
            "latitude": data["area_latitude"],
            "longitude": data["area_longitude"],
            "systems": data["systems"]
        }


 # def get_image_bmp(self, obj):
    #     img = Image.open(obj.image)
        
    #     # new_width = int(self.context['request'].GET.get('width', img.width))
    #     # new_height = int(self.context['request'].GET.get('height', img.height))
 
    #     new_width= 100
    #     new_height= 100
    #     img = img.resize((new_width, new_height))

    #     img_bmp = img.convert('RGB')

    #     buffer = io.BytesIO()
    #     img_bmp.save(buffer, format='BMP')
    #     # img_bmp_base64 = base64.b64encode(buffer.getvalue()).decode()
    #     return buffer.getvalue()