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
    QueryParamsSerializer,
    WelcomeModelSerializer,
    YourCollectionModelSerializer,
)


class QueryParametersMixin:
    def get_serializer_context(self):
        context = super().get_serializer_context()
        serialized_query_params = QueryParamsSerializer(data=self.request.query_params)
        if serialized_query_params.is_valid():
            query_params = serialized_query_params.data
        else:
            query_params = {}
        context.update(query_params=query_params)
        return context


class SingletonMixin:
    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            return Response(status=204)
        else:
            return Response(serializer.data[0])


class WelcomeViewSet(QueryParametersMixin, SingletonMixin, ReadOnlyModelViewSet):
    serializer_class = WelcomeModelSerializer
    queryset = Welcome.objects.all()


class CharacterOverviewViewSet(
    QueryParametersMixin, SingletonMixin, ReadOnlyModelViewSet
):
    serializer_class = CharacterOverviewModelSerializer
    queryset = CharacterOverview.objects.all()


class ChooseCharacterViewSet(QueryParametersMixin, ReadOnlyModelViewSet):
    serializer_class = ChooseCharacterModelSerializer
    queryset = ChooseCharacter.objects.all()


class IntroSearchAndCollectViewSet(QueryParametersMixin, ReadOnlyModelViewSet):
    serializer_class = IntroSearchAndCollectModelSerializer
    queryset = IntroSearchAndCollect.objects.all()


class PhotographyScreenViewSet(QueryParametersMixin, ReadOnlyModelViewSet):
    serializer_class = PhotographyScreenModelSerializer
    queryset = PhotographyScreen.objects.all()


class YourCollectionViewSet(QueryParametersMixin, ReadOnlyModelViewSet):
    serializer_class = YourCollectionModelSerializer
    queryset = YourCollection.objects.all()
