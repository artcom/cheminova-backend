from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import (
    CharacterOverview,
    ChooseCharacter,
    IntroSearchAndCollect,
    PhotographyScreen,
    Welcome,
    YourCollection,
)
from .serializers import (
    CharacterOverviewModelSerializer,
    ChooseCharacterModelSerializer,
    IntroSearchAndCollectModelSerializer,
    PhotographyScreenModelSerializer,
    WelcomeModelSerializer,
    YourCollectionModelSerializer,
)


class WelcomeViewSet(ReadOnlyModelViewSet):
    serializer_class = WelcomeModelSerializer
    queryset = Welcome.objects.all()

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            return Response(status=204)
        else:
            return Response(serializer.data[0])


class CharacterOverviewViewSet(ReadOnlyModelViewSet):
    serializer_class = CharacterOverviewModelSerializer
    queryset = CharacterOverview.objects.all()

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            return Response(status=204)
        else:
            return Response(serializer.data[0])


class ChooseCharacterViewSet(ReadOnlyModelViewSet):
    serializer_class = ChooseCharacterModelSerializer
    queryset = ChooseCharacter.objects.all()


class IntroSearchAndCollectViewSet(ReadOnlyModelViewSet):
    serializer_class = IntroSearchAndCollectModelSerializer
    queryset = IntroSearchAndCollect.objects.all()


class PhotographyScreenViewSet(ReadOnlyModelViewSet):
    serializer_class = PhotographyScreenModelSerializer
    queryset = PhotographyScreen.objects.all()


class YourCollectionViewSet(ReadOnlyModelViewSet):
    serializer_class = YourCollectionModelSerializer
    queryset = YourCollection.objects.all()
