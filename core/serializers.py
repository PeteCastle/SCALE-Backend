from rest_framework import serializers

from core.models import Images, System, Images, AreaCoverage, SystemWaterLevel
import time

from rcnn.predictor import RCNNPredictor

class MosquitoImagesSerializer(serializers.ModelSerializer):
    # image_bmp = serializers.SerializerMethodField()
    secret_key = serializers.CharField(write_only=True)
    count = serializers.SerializerMethodField()

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
        validated_data["photo"], validated_data['detected_mosquito_count'] = RCNNPredictor()(validated_data["photo"], validated_data["system"])
        end_time = time.time()
        validated_data['prediction_time'] = end_time - start_time
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