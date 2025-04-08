import uuid
from pathlib import Path

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import ImageModelSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def upload_image_view(request):
    file = request.data.get("image")
    title = file.name
    file_path = Path(file.name)
    file.name = file_path.stem + f"-{uuid.uuid4()}" + file_path.suffix
    data = {
        "file": file,
        "title": title,
        "hidden": True,
    }
    serializer = ImageModelSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            data=serializer.data,
            status=201,
            headers={"Location": serializer.data["file"]}
        )
    else:
        return Response(
            data=serializer.errors,
            status=400
        )
