from django.db import models  # noqa
from rest_framework import serializers
from wagtail.images import get_image_model


class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_image_model()
        fields = ["file", "title", "collection"]
