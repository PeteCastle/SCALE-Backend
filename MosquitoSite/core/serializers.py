from rest_framework import serializers

from core.models import MosquitoImages

class MosquitoImagesSerializer(serializers.ModelSerializer):
    secret_key = serializers.CharField(write_only=True)

    class Meta:
        model = MosquitoImages
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

    