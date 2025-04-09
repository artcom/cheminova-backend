from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Home
from .serializers import HomeModelSerializer


class HomeViewSet(ReadOnlyModelViewSet):
    serializer_class = HomeModelSerializer
    queryset = Home.objects.all()

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data[0])
