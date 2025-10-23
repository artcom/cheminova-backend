from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from wagtail.images import get_image_model
from wagtail.images.models import Image
from wagtail.permission_policies.collections import CollectionPermissionPolicy

from experience.models import Character

from .serializers import (
    CustomImageModelSerializer,
    ImageUploadRequestSerializer,
    SaveImageModelSerializer,
)


class AllowCharacterImages(BasePermission):
    """
    Custom permission to allow access to character images.
    """

    def has_permission(self, request, view):
        return view.kwargs.get("character") is not None


class ImageViewSet(ModelViewSet):
    """
    A viewset for listing and uploading custom images associated with characters.
    """

    permission_classes = [IsAuthenticated | AllowCharacterImages]
    serializer_class = CustomImageModelSerializer
    queryset = get_image_model().objects.all()
    lookup_url_kwarg = "character"

    def get_queryset(self):
        character = self.kwargs.get(self.lookup_url_kwarg)
        allowed_collections = []
        if self.request.user.is_authenticated:
            permission_policy = CollectionPermissionPolicy(
                get_image_model(), auth_model=Image
            )
            allowed_collections.extend(
                list(
                    permission_policy.collections_user_has_any_permission_for(
                        self.request.user, ["change", "add", "delete", "choose"]
                    )
                )
            )

        if character is not None:
            try:
                character_instance = Character.objects.get(slug=character)
                collections = [character_instance.approved_collection]
                if character_instance.not_approved_collection in allowed_collections:
                    collections.append(character_instance.not_approved_collection)
                return self.queryset.filter(collection__in=collections)

            except Character.DoesNotExist:
                return self.queryset.none()

        return self.queryset.filter(collection__in=allowed_collections)

    def create(self, request, *args, **kwargs):
        character = kwargs.get(self.lookup_url_kwarg)
        try:
            character_instance = Character.objects.get(slug=character)
        except Character.DoesNotExist:
            return Response(data={"error": "Character not found"}, status=404)

        request_serializer = ImageUploadRequestSerializer(data=request.data)

        if not request_serializer.is_valid():
            return Response(data=request_serializer.errors, status=400)

        data = {
            **request_serializer.validated_data,
            "collection": character_instance.not_approved_collection.pk,
        }

        image_serializer = SaveImageModelSerializer(data=data)

        if image_serializer.is_valid():
            image_serializer.save()
            return Response(
                data=image_serializer.data,
                status=201,
                headers={"Location": image_serializer.data["file"]},
            )

        else:
            return Response(
                data={**image_serializer.errors, "error": "Image upload failed"},
                status=400,
            )
