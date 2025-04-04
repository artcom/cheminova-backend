from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import CustomImage
from .serializers import CustomImageModelSerializer


class CustomImageViewSet(ReadOnlyModelViewSet):
    serializer_class = CustomImageModelSerializer
    queryset = CustomImage.objects.all()
