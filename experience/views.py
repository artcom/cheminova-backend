from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

import experience.models as experience_models
import experience.serializers as experience_serializers

from .serializers import QueryParamsSerializer


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


def create_model_viewset(model_name):
    serializer_class = getattr(experience_serializers, f"{model_name}ModelSerializer")
    model = getattr(experience_models, model_name)
    queryset = model.objects.all()

    if model.max_count == 1:
        mixins = (QueryParametersMixin, SingletonMixin)
    else:
        mixins = (QueryParametersMixin,)

    return type(
        f"{model_name}ViewSet",
        (*mixins, ReadOnlyModelViewSet),
        {
            "serializer_class": serializer_class,
            "queryset": queryset,
        },
    )


for model_name in experience_models.__all__:
    globals()[f"{model_name}ViewSet"] = create_model_viewset(model_name)
