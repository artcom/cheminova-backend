from django.conf import settings
from django.db import models  # noqa
from rest_framework import serializers

from .models import CustomImage


class RenditionFileField(serializers.RelatedField):
    def to_representation(self, value):
        return settings.WAGTAILADMIN_BASE_URL + str(value.file.url)


class CustomImageModelSerializer(serializers.ModelSerializer):
    renditions = RenditionFileField(many=True, read_only=True)

    class Meta:
        model = CustomImage
        fields = ["id", "title", "file", "public", "renditions"]
        depth = 1
