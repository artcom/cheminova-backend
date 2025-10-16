import uuid
from pathlib import PurePath

from django.db import models  # noqa
from rest_framework import serializers
from wagtail.images import get_image_model
from wagtail.models.media import Collection


class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_image_model()
        fields = ["file", "title", "collection"]


class ImageFieldWithUniqueName(serializers.ImageField):
    def to_internal_value(self, data):
        file = super().to_internal_value(data)
        if file:
            original_name = file.name
            file_path = PurePath(original_name)
            file.name = file_path.stem + f"-{uuid.uuid4()}" + file_path.suffix
        return {"file": file, "title": original_name}


class CharacterField(serializers.CharField):
    def to_internal_value(self, data):
        character = super().to_internal_value(data)
        try:
            parent_collection = Collection.objects.get(name=character)
            not_approved_collection = parent_collection.get_children().get(
                name="Not Approved"
            )
            return {"name": character, "default_collection": not_approved_collection.pk}
        except Collection.DoesNotExist:
            raise serializers.ValidationError("Invalid character name.")


class ImageUploadRequestSerializer(serializers.Serializer):
    image = ImageFieldWithUniqueName(required=True)
    character = CharacterField(required=True)
