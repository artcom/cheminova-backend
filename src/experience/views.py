from rest_framework.viewsets import ReadOnlyModelViewSet
from wagtail.models import Locale

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

    default_params = {"depth": 0, "browsable": "true"}

    def get_serializer_context(self):
        context = super().get_serializer_context()
        query_params = self.default_params.copy()
        serialized_query_params = QueryParamsSerializer(data=self.request.query_params)
        if serialized_query_params.is_valid():
            query_params.update(serialized_query_params.data)
        context.update(query_params=query_params)
        return context


class FilterLocaleMixin:
    """
    Mixin that filters queryset by 'locale' query parameter if provided.

    If 'locale' is specified in query parameters, the queryset is filtered to
    include only objects matching that locale. Otherwise, the full queryset is returned.

    Example: GET /api/choose-character/?locale=en returns only English characters.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        locale = self.request.query_params.get("locale")
        if locale:
            locale_query = Locale.objects.filter(language_code=locale).first()
            locale_id = locale_query.id if locale_query else None
            queryset = queryset.filter(locale=locale_id) if locale_id else queryset
        return queryset


def create_model_viewset(model_name):
    """
    Factory function that dynamically creates ViewSet classes for experience models.

    This function generates specialized read-only ViewSets for experience models by
    introspecting the model structure and automatically configuring the appropriate
    mixins and serializers. The resulting ViewSets provide REST API endpoints with
    query parameter support.

    Args:
        model_name (str): The name of the model class from experience_models module
                         (must be present in experience_models.__all__)

    Returns:
        type: A dynamically created ViewSet class with the following features:
              - ReadOnlyModelViewSet base functionality (GET operations only)
              - QueryParametersMixin for depth control and other query params
              - Appropriate serializer class auto-configured
              - Queryset configured for the specific model

    Example:
        # The resulting ViewSet class is equivalent to:
        class WelcomeViewSet(QueryParametersMixin, ReadOnlyModelViewSet):
            serializer_class = WelcomeModelSerializer
            queryset = Welcome.objects.all()

            # GET /api/welcome/ returns list of Welcome objects (not a single object)
            # GET /api/welcome/?depth=2 includes nested children up to depth 2
            # GET /api/welcome/?locale=en filters Welcome objects to English locale
    """
    serializer_class = getattr(experience_serializers, f"{model_name}ModelSerializer")
    model = getattr(experience_models, model_name)
    queryset = model.objects.all()
    mixins = (QueryParametersMixin, FilterLocaleMixin)

    return type(
        f"{model_name}ViewSet",
        (*mixins, ReadOnlyModelViewSet),
        {
            "serializer_class": serializer_class,
            "queryset": queryset,
        },
    )


class AllModelViewSet(QueryParametersMixin, FilterLocaleMixin, ReadOnlyModelViewSet):
    serializer_class = getattr(experience_serializers, "WelcomeLanguageModelSerializer")
    serializer_class.Meta.fields.remove("selfUrl")
    queryset = experience_models.WelcomeLanguage.objects.all()
    default_params = {"depth": None, "browsable": "false"}


# Dynamically create and register ViewSet classes for all experience models
for model_name in experience_models.__all__:
    viewset = create_model_viewset(model_name)
    globals()[viewset.__name__] = viewset
