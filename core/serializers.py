from rest_framework import serializers

from core.models import Images, System, Images, AreaCoverage

class MosquitoImagesSerializer(serializers.ModelSerializer):
    secret_key = serializers.CharField(write_only=True)

    class Meta:
        model = Images
        fields = [
            "image",
            "secret_key",
        ]
        # fields = [
        #     "id",
        #     "content",
        #     "parent_comment",
        #     "uploaded_images",
        #     "anonymous",
        # ]   

    # def create(self, validated_data):
    #     reply_data = validated_data.copy()
    #     if reply_data.get("uploaded_images"):
    #         reply_data.pop("uploaded_images")

    #     reply = Comment.objects.create(**reply_data)

    #     if validated_data.get("uploaded_images"):
    #         uploaded_images = validated_data.pop("uploaded_images")
    #         for image in uploaded_images:
    #             UserMedia.objects.create(reply=reply, image=image, author=reply.author)
        
    #     return reply
    
    # def validate(self, fields):
    #     # if not fields.get("project"):
    #     #     raise serializers.ValidationError("Project ID is required.")

    #     if fields.get("uploaded_images"):
    #         if len(fields.get("uploaded_images")) > 5:
    #             raise serializers.ValidationError("You can only upload a maximum of 5 images.")
    #     return fields
    
    
    # def run_validation(self, data=...):
    #     data = data.copy()
  
    #     try:
    #         if data.get("uploaded_images") == "":
    #             data.pop("uploaded_images")
    #     except MultiValueDictKeyError:
    #         data.pop("uploaded_images")
    #     return super().run_validation(data)

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
