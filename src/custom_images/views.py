from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from wagtail.models.media import Collection

from .models import CustomImage
from .serializers import CustomImageModelSerializer


class ImageViewSet(ReadOnlyModelViewSet):
    """
    A viewset for listing images. Only authenticated users can access this endpoint.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CustomImageModelSerializer
    queryset = CustomImage.objects.all()
    lookup_url_kwarg = "character"

    def get_queryset(self):
        character = self.kwargs.get(self.lookup_url_kwarg)
        if character is not None:
            try:
                collection = Collection.objects.get(
                    name__iexact=character.replace("-", " ")
                )
                return self.queryset.filter(
                    collection__in=collection.get_descendants(inclusive=True)
                )
            except Collection.DoesNotExist:
                return self.queryset.none()
        return self.queryset

    @action(detail=False, permission_classes=[AllowAny])
    def approved(self, *args, **kwargs) -> Response:
        """
        Returns a list of all approved images for a character.
        """
        character = self.kwargs.get("character")
        try:
            parent_collection = Collection.objects.get(
                name__iexact=character.replace("-", " ")
            )
            approved_collection = parent_collection.get_children().get(name="Approved")
            images = self.queryset.filter(collection=approved_collection)
            serializer = self.get_serializer(images, many=True)
            return Response(serializer.data)
        except Collection.DoesNotExist:
            return Response([])
