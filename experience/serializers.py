import urllib

from caseutil import to_camel, to_kebab, to_snake
from django.conf import settings
from django.db import models  # noqa
from modelcluster.models import get_all_child_relations
from rest_framework import serializers
from wagtail.images import get_image_model

import experience.models as experience_models


def absolute_url(relative_url: str) -> str:
    return settings.WAGTAILADMIN_BASE_URL + relative_url


def format_is_api(context: dict) -> bool:
    return context.get("query_params", {}).get("format") == "api" or not context.get(
        "query_params", {}
    ).get("format")


def query_params_string(context: dict) -> str:
    return (
        f"?{urllib.parse.urlencode(context.get('query_params'))}"
        if format_is_api(context) and context.get("query_params")
        else ""
    )


def serialize(obj: models.Model) -> serializers.ModelSerializer:
    return globals()[f"{obj.__class__.__name__}ModelSerializer"](obj)


def get_serialized_data(child: models.Model, context: dict) -> dict:
    serializer = serialize(child)
    serializer.context.update(context)
    if context.get("no_self_url"):
        data = serializer.data
        data.pop("selfUrl", None)
        return data
    else:
        return serializer.data


def endpoint(obj: models.Model) -> str:
    return f"/{to_kebab(obj.__class__.__name__)}"


def to_camel_case_data(data: dict) -> dict:
    return {to_camel(key): value for key, value in data.items()}


def to_snake_case_data(data: dict) -> dict:
    return {to_snake(key): value for key, value in data.items()}


class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_image_model()
        fields = ["file"]


class CamelCaseMixin:
    def to_representation(self, *args, **kwargs):
        return to_camel_case_data(super().to_representation(*args, **kwargs))

    def to_internal_value(self, data):
        return super().to_internal_value(to_snake_case_data(data))


class PageModelSerializer(CamelCaseMixin, serializers.ModelSerializer):
    """
    Base serializer for Wagtail Page models with hierarchical structure support.

    This serializer extends Django REST framework's ModelSerializer with camelCase
    conversion and adds functionality for handling page hierarchies. It provides
    self-referencing URLs and nested children serialization with configurable depth.

    Attributes:
        selfUrl (SerializerMethodField): Generates the API endpoint URL for the page
        children (SerializerMethodField): Serializes child pages with depth control

    Query Parameters:
        depth (int, optional): Limits the depth of children serialization.
                              When specified, children beyond this depth return URLs only.
    """

    children = serializers.SerializerMethodField()
    locale = serializers.CharField(source="locale.language_code", read_only=True)

    def get_children(self, obj: models.Model) -> list:
        children = obj.get_children().live().specific()
        self.context.update(no_self_url=True)
        return [get_serialized_data(child, self.context) for child in children]


class BrowsablePageModelSerializer(PageModelSerializer):
    selfUrl = serializers.SerializerMethodField()

    def get_selfUrl(self, obj: models.Model) -> str:
        return f"{absolute_url(settings.API_BASE_URL + endpoint(obj) + f'/{obj.id}')}{query_params_string(self.context)}"

    def get_children_urls(self, obj: models.Model) -> list:
        children = obj.get_children().live().specific()
        children_urls = [
            data.get("selfUrl")
            for data in [get_serialized_data(child, self.context) for child in children]
        ]
        return children_urls

    def get_children(self, obj: models.Model) -> list:
        query_params = self.context.get("query_params", {})
        if query_params.get("depth") is not None:
            if not self.context.get("iteration"):
                self.context.update(iteration=0)
            if self.context["iteration"] >= int(query_params.get("depth")):
                return self.get_children_urls(obj)
            else:
                children = obj.get_children().live().specific()
                self.context.update(iteration=self.context.get("iteration", 0) + 1)
                return [get_serialized_data(child, self.context) for child in children]
        else:
            children = obj.get_children().live().specific()
            return [get_serialized_data(child, self.context) for child in children]


def create_model_cluster_serializer(related_model: models.Model):
    """
    Factory function that creates serializers for model cluster relationship models.

    This function generates specialized serializers for models that are related to
    Page models through ParentalKey relationships (model clusters). These are typically
    used for inline content like ordered lists, repeatable content blocks, or
    related data that belongs to a specific page.

    Args:
        related_model (Model): The Django model class that has a ParentalKey relationship
                              to a Page model (must have api_fields attribute)

    Returns:
        type: A dynamically created serializer class with the following features:
              - Inherits from CamelCaseMixin and ModelSerializer
              - CamelCase field name conversion
              - Meta class configured with the model's api_fields
              - Named as "{ModelName}ModelClusterSerializer"

    Example:
        # The resulting serializer class is equivalent to:
        class ImageDescriptionModelClusterSerializer(CamelCaseMixin, serializers.ModelSerializer):
            class Meta:
                model = ImageDescription
                fields = ["description"]  # From ImageDescription.api_fields

    Note:
        This function is used internally by create_model_serializer to handle
        nested relationships when a Page model has inline/related content.
    """

    class Meta:
        model = related_model
        fields = related_model.api_fields

    return type(
        f"{related_model.__name__}ModelClusterSerializer",
        (
            CamelCaseMixin,
            serializers.ModelSerializer,
        ),
        {
            "Meta": Meta,
        },
    )


def create_model_serializer(model_name: str):
    """
    Factory function that dynamically creates model serializers for Wagtail Page models.

    This function generates specialized serializers for experience models by introspecting
    the model structure and automatically configuring serialization for image fields and
    model cluster relationships. The resulting serializers inherit from PageModelSerializer
    and include proper handling for nested relationships.

    Args:
        model_name (str): The name of the model class from experience_models module
                         (must be present in experience_models.__all__)

    Returns:
        type: A dynamically created serializer class that inherits from PageModelSerializer
              with the following features:
              - Image fields serialized using ImageModelSerializer
              - Model cluster relationships serialized with many=True
              - CamelCase field conversion
              - Self-referencing URLs and children support
              - Meta class configured with model's api_fields

    Example:
        # The resulting serializer class is equivalent to:
        class WelcomeModelSerializer(PageModelSerializer):
            background_image = ImageModelSerializer()  # Auto-detected image field

            class Meta:
                model = Welcome
                fields = [
                    "title", "description", "site_name", "background_image",  # From Welcome.api_fields
                    "children", "selfUrl"  # Added by PageModelSerializer
                ]

        # For models with cluster relationships like YourCollection:
        class YourCollectionModelSerializer(PageModelSerializer):
            image_descriptions = ImageDescriptionModelClusterSerializer(many=True)

            class Meta:
                model = YourCollection
                fields = ["title", "heading", "image_descriptions", "children", "selfUrl"]
    """

    serializer_model = getattr(experience_models, model_name)
    page_model_serializer_extra_fields = [
        "locale",
        "children",
        "selfUrl",
    ]
    image_field_names = [
        field.name
        for field in serializer_model._meta.get_fields()
        if isinstance(field, models.fields.related.ForeignKey)
        and field.related_model == get_image_model()
    ]
    image_fields = {name: ImageModelSerializer() for name in image_field_names}
    model_cluster_relations = [
        (
            relation.related_name,
            relation.related_model,
        )
        for relation in get_all_child_relations(serializer_model)
        if relation.model == serializer_model
    ]
    model_cluster_fields = {
        related_name: create_model_cluster_serializer(related_model)(many=True)
        for related_name, related_model in model_cluster_relations
    }

    class Meta:
        model = serializer_model
        fields = serializer_model.api_fields + page_model_serializer_extra_fields

    return type(
        f"{model_name}ModelSerializer",
        (BrowsablePageModelSerializer,),
        {
            **image_fields,
            **model_cluster_fields,
            "Meta": Meta,
        },
    )


class AllModelSerializer(PageModelSerializer):
    background_image = ImageModelSerializer()

    class Meta:
        model = experience_models.Welcome
        fields = [
            "title",
            "description",
            "site_name",
            "background_image",
            "locale",
            "children",
        ]


# Dynamically create and register serializer classes for all experience models
for model_name in experience_models.__all__:
    model = create_model_serializer(model_name)
    globals()[model.__name__] = model


class QueryParamsSerializer(serializers.Serializer):
    depth = serializers.IntegerField(required=False)
    format = serializers.CharField(required=False)
    locale = serializers.CharField(required=False)
