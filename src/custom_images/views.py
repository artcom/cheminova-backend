from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from experience.models import Character

from .models import CustomImage
from .serializers import (
    CustomImageModelSerializer,
    ImageModelSerializer,
    ImageUploadRequestSerializer,
)


class AllowApproved(BasePermission):
    """
    Custom permission to allow access to character images.
    """

    def has_permission(self, request, view):
        return view.kwargs.get("character") is not None


class ImageViewSet(ModelViewSet):
    """
    A viewset for listing and uploading custom images associated with characters.
    """

    permission_classes = [IsAuthenticated | AllowApproved]
    serializer_class = CustomImageModelSerializer
    queryset = CustomImage.objects.all()
    lookup_url_kwarg = "character"

    def get_queryset(self):
        character = self.kwargs.get(self.lookup_url_kwarg)
        if character is not None:
            try:
                character_instance = Character.objects.get(slug=character)
                if self.request.user.is_authenticated:
                    return self.queryset.filter(
                        collection__in=[
                            character_instance.approved_collection,
                            character_instance.not_approved_collection,
                        ]
                    )
                else:
                    return self.queryset.filter(
                        collection=character_instance.approved_collection
                    )
            except Character.DoesNotExist:
                return self.queryset.none()
        return self.queryset

    def create(self, request, *args, **kwargs):
        character = self.kwargs.get(self.lookup_url_kwarg)
        if character is not None:
            try:
                character_instance = Character.objects.get(slug=character)
            except Character.DoesNotExist:
                return Response(data={"error": "Character not found"}, status=404)
        request_serializer = ImageUploadRequestSerializer(data=request.data)

        if not request_serializer.is_valid():
            return Response(data=request_serializer.errors, status=400)

        image = request_serializer.validated_data["image"]

        data = {
            "file": image["file"],
            "title": image["title"],
            "collection": character_instance.not_approved_collection.pk,
        }

        image_serializer = ImageModelSerializer(data=data)

        if image_serializer.is_valid():
            image_serializer.save()
            return Response(
                data=image_serializer.data,
                status=201,
                headers={"Location": image_serializer.data["file"]},
            )

        else:
            return Response(data=image_serializer.errors, status=400)
