import uuid
from pathlib import PurePath

from django.conf import settings
from django.db import models  # noqa
from rest_framework import serializers

from .models import CustomImage


class RenditionFileField(serializers.RelatedField):
    def to_representation(self, value):
        return settings.WAGTAILADMIN_BASE_URL + value.file.url


class CustomImageModelSerializer(serializers.ModelSerializer):
    renditions = RenditionFileField(many=True, read_only=True)
    live = serializers.SerializerMethodField()
    collection = serializers.CharField(source="collection.name", read_only=True)

    class Meta:
        model = CustomImage
        fields = [
            "id",
            "title",
            "file",
            "renditions",
            "live",
            "collection",
            "uploaded_text",
            "uploaded_user_name",
            "created_at",
        ]
        depth = 0

    def get_live(self, obj: CustomImage) -> bool:
        return len(obj.get_referenced_live_pages()) > 0


class SaveImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomImage
        fields = ["file", "title", "collection", "uploaded_text", "uploaded_user_name"]


class ImageFieldWithUniqueName(serializers.ImageField):
    def to_internal_value(self, data):
        file = super().to_internal_value(data)
        if file:
            original_name = file.name
            file_path = PurePath(original_name)
            file.name = file_path.stem + f"-{uuid.uuid4()}" + file_path.suffix
        return {"file": file, "title": original_name}


class ImageUploadRequestSerializer(serializers.Serializer):
    image = ImageFieldWithUniqueName(required=True)
    text = serializers.CharField(required=False, allow_blank=True)
    userName = serializers.CharField(required=False, allow_blank=True)

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        return {
            "file": ret["image"]["file"],
            "title": ret["image"]["title"],
            "uploaded_text": ret.get("text", ""),
            "uploaded_user_name": ret.get("userName", ""),
        }
