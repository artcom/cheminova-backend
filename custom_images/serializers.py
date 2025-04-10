from django.conf import settings
from django.db import models  # noqa
from rest_framework import serializers
from wagtail.models import Page
from .models import CustomImage


class RenditionFileField(serializers.RelatedField):
    def to_representation(self, value):
        return settings.WAGTAILADMIN_BASE_URL + value.file.url


class CustomImageModelSerializer(serializers.ModelSerializer):
    renditions = RenditionFileField(many=True, read_only=True)
    live = serializers.SerializerMethodField()

    class Meta:
        model = CustomImage
        fields = ["id", "title", "file", "public", "renditions", "live"]
        depth = 1

    def get_live(self, obj: CustomImage) -> bool:
        if len(obj.get_usage()) > 0:
            referenced_live_pages = [reference_index[0]
                                     for reference_index in obj.get_usage()
                                     if isinstance(reference_index[0], Page)
                                     and reference_index[0].live]
            return len(referenced_live_pages) > 0
        else:
            return False
