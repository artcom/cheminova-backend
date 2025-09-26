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

    class Meta:
        model = CustomImage
        fields = ["id", "title", "file", "renditions", "live"]
        depth = 1

    def get_live(self, obj: CustomImage) -> bool:
        return len(obj.get_referenced_live_pages()) > 0
