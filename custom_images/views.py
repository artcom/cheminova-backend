from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import CustomImage
from .serializers import CustomImageModelSerializer


class CustomImageViewSet(ReadOnlyModelViewSet):
    """
    A viewset for listing images. All authenticated users are allowed to view images. Anonymous
    users can only view images referenced by a live page.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CustomImageModelSerializer
    queryset = CustomImage.objects.all()
