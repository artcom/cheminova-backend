from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import ImageModelSerializer, ImageUploadRequestSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def upload_image_view(request: Request) -> Response:
    request_serializer = ImageUploadRequestSerializer(data=request.data)
    if not request_serializer.is_valid():
        return Response(data=request_serializer.errors, status=400)

    image = request_serializer.validated_data["image"]
    character = request_serializer.validated_data["character"]

    data = {
        "file": image["file"],
        "title": image["title"],
        "collection": character["default_collection"],
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
