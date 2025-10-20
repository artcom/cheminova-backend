import uuid
from pathlib import PurePath

from django.conf import settings
from django.db import models  # noqa
from rest_framework import serializers

from experience.models import Character

from .models import CustomImage


class RenditionFileField(serializers.RelatedField):
    def to_representation(self, value):
        return settings.WAGTAILADMIN_BASE_URL + value.file.url


class CustomImageModelSerializer(serializers.ModelSerializer):
    renditions = RenditionFileField(many=True, read_only=True)
    live = serializers.SerializerMethodField()
    character = serializers.SerializerMethodField()
    collection = serializers.CharField(source="collection.name")

    class Meta:
        model = CustomImage
        fields = [
            "id",
            "title",
            "file",
            "renditions",
            "live",
            "collection",
            "character",
        ]
        depth = 0

    def get_live(self, obj: CustomImage) -> bool:
        return len(obj.get_referenced_live_pages()) > 0

    def get_character(self, obj: CustomImage) -> str:
        character_for_collection = Character.objects.filter(
            models.Q(approved_collection=obj.collection)
            | models.Q(not_approved_collection=obj.collection)
        ).first()
        if character_for_collection:
            return character_for_collection.name
        return None


class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomImage
        fields = ["file", "title", "collection"]


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
