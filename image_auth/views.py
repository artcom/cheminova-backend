import re

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from wagtail.images import get_image_model

from custom_images.models import CustomRendition


@api_view(["GET"])
@permission_classes([AllowAny])
def check_permissions(request: Request) -> Response:
    """
    A view to check if the user has permission to view images. All users are allowed to view images
    that do not have the hidden flag set to True. Only authenticated users can view images with the
    hidden flag set to True.
    """
    if request.user.is_authenticated:
        return Response(
            data={"message": "OK"},
            status=200
        )

    else:
        if not request.headers.get("X-Original-Uri"):
            return Response(
                data={"message": "Bad Request"},
                status=400
            )

        requested_image = get_image_file(request.headers.get("X-Original-Uri"))
        image_type = get_image_type(requested_image)

        if not image_type:
            return Response(
                data={"message": "Bad Request"},
                status=400
            )

        match image_type:
            case "rendition":
                try:
                    db_image = CustomRendition.objects.get(file=requested_image).image
                except CustomRendition.DoesNotExist:
                    return Response(
                        data={"message": "Not found"},
                        status=404
                    )

            case "original":
                Image = get_image_model()
                try:
                    db_image = Image.objects.get(file=requested_image)
                except Image.DoesNotExist:
                    return Response(
                        data={"message": "Not found"},
                        status=404
                    )

        if not db_image.hidden:
            return Response(
                {"message": "OK"},
                status=200
            )

        return Response(
            data={"message": "Unauthorized"},
            status=401
        )


def get_image_file(image_url: str) -> str:
    """
    Get the original image file from the image URL.
    """
    return image_url.replace(settings.MEDIA_URL, "")


def get_image_type(image: str) -> str | None:
    """
    Check if the image is a rendition.
    """
    if re.match(r"^images/", image):
        return "rendition"
    elif re.match(r"^original_images/", image):
        return "original"
    else:
        return None
