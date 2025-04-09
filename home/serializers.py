from django.conf import settings
from django.db import models  # noqa
from rest_framework import serializers

from .models import Home


class HomeModelSerializer(serializers.ModelSerializer):
    imageUrl = serializers.SerializerMethodField()

    class Meta:
        model = Home
        fields = ['id', 'title', 'imageUrl']
        depth = 1

    def get_imageUrl(self, obj: Home) -> str:
        return settings.WAGTAILADMIN_BASE_URL + obj.image.file.url
