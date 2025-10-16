from rest_framework.routers import DynamicRoute, Route, SimpleRouter

from custom_images.views import ImageViewSet


class CustomReadOnlyRouter(SimpleRouter):
    """
    A router for read-only APIs, which doesn't use trailing slashes.
    """

    routes = [
        Route(
            url=r"^{prefix}{trailing_slash}$",
            mapping={"get": "list"},
            name="{basename}-list",
            detail=False,
            initkwargs={"suffix": "List"},
        ),
        Route(
            url=r"^{prefix}/{lookup}{trailing_slash}$",
            mapping={"get": "list"},
            name="{basename}-character",
            detail=False,
            initkwargs={"suffix": "Character"},
        ),
        DynamicRoute(
            url=r"^{prefix}/{lookup}/{url_path}{trailing_slash}$",
            name="{basename}-{url_name}",
            detail=False,
            initkwargs={},
        ),
    ]


router = CustomReadOnlyRouter()
router.register("images", ImageViewSet)
urlpatterns = router.urls
