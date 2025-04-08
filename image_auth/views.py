import re

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from wagtail.images import get_image_model

from custom_images.models import CustomRendition


@api_view(["GET"])
@permission_classes([AllowAny])
def check_permissions(request):
    """
    A view to check if the user has permission to view images. All users are allowed to view images
    that do not have the hidden flag set to True. Only authenticated users can view images with the
    hidden flag set to True.
    """
    if request.user.is_authenticated:
        return Response({"message": "OK"}, status=200)
    else:
        Image = get_image_model()
        requested_image = get_image_file(
            request.headers.get("X-Original-Uri"))
        if not requested_image:
            return Response({"message": "Bad Request"}, status=400)
        if re.match(r"^images/", requested_image):
            try:
                db_image = CustomRendition.objects.get(file=requested_image).image
            except CustomRendition.DoesNotExist:
                return Response({"message": "Not found"}, status=404)
        elif re.match(r"^original_images/", requested_image):
            try:
                db_image = Image.objects.get(file=requested_image)
            except Image.DoesNotExist:
                return Response({"message": "Not found"}, status=404)
        if not db_image.hidden:
            return Response({"message": "OK"}, status=200)
        else:
            return Response({"message": "Unauthorized"}, status=401)


def get_image_file(image_url):
    """
    Get the original image URL from the image URL.
    """
    return image_url.replace(settings.MEDIA_URL, "")
