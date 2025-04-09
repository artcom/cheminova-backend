from django.conf import settings
from django.db import models  # noqa
from rest_framework import serializers

from .models import CustomImage


class CustomImageModelSerializer(serializers.ModelSerializer):
    imageUrl = serializers.SerializerMethodField()

    class Meta:
        model = CustomImage
        fields = ['id', 'title', 'imageUrl', 'file', 'hidden']
        depth = 1

    def get_imageUrl(self, obj: CustomImage) -> str:
        return settings.WAGTAILADMIN_BASE_URL + obj.file.url
