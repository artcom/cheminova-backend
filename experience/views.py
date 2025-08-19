from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

import experience.models as experience_models
import experience.serializers as experience_serializers

from .serializers import QueryParamsSerializer


class QueryParametersMixin:
    """
    Mixin that validates query parameters and adds them to serializer context.

    Validates query parameters using QueryParamsSerializer and makes them
    available to serializers. Supports depth control for nested serialization.

    Example: GET /api/welcome/?depth=2 limits children nesting to 2 levels.
    """

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
    """
    Mixin that returns a single object instead of a list for singleton models.

    Overrides the list method to return the first object directly or 204 No Content
    if no objects exist. Used for models with max_count=1 like Welcome pages.
    """

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        if not serializer.data:
            return Response(status=204)
        else:
            return Response(serializer.data[0])


def create_model_viewset(model_name):
    """
    Factory function that dynamically creates ViewSet classes for experience models.

    This function generates specialized read-only ViewSets for experience models by
    introspecting the model structure and automatically configuring the appropriate
    mixins and serializers. The resulting ViewSets provide REST API endpoints with
    query parameter support and singleton behavior for models with max_count=1.

    Args:
        model_name (str): The name of the model class from experience_models module
                         (must be present in experience_models.__all__)

    Returns:
        type: A dynamically created ViewSet class with the following features:
              - ReadOnlyModelViewSet base functionality (GET operations only)
              - QueryParametersMixin for depth control and other query params
              - SingletonMixin for models with max_count=1 (returns single object)
              - Appropriate serializer class auto-configured
              - Queryset configured for the specific model

    Example:
        # The resulting ViewSet class is equivalent to:
        class WelcomeViewSet(QueryParametersMixin, SingletonMixin, ReadOnlyModelViewSet):
            serializer_class = WelcomeModelSerializer
            queryset = Welcome.objects.all()

            # GET /api/welcome/ returns single Welcome object (not a list)
            # GET /api/welcome/?depth=2 includes nested children up to depth 2

        # For non-singleton models like ChooseCharacter:
        class ChooseCharacterViewSet(QueryParametersMixin, ReadOnlyModelViewSet):
            serializer_class = ChooseCharacterModelSerializer
            queryset = ChooseCharacter.objects.all()

            # GET /api/choose-character/ returns list of ChooseCharacter objects
            # GET /api/choose-character/1/ returns specific ChooseCharacter object
    """
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


# Dynamically create and register ViewSet classes for all experience models
for model_name in experience_models.__all__:
    viewset = create_model_viewset(model_name)
    globals()[viewset.__name__] = viewset
