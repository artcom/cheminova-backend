from rest_framework.routers import Route, SimpleRouter

from custom_images.views import ImageViewSet


class CustomRouter(SimpleRouter):
    """
    A router for read-only APIs.
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
            mapping={"get": "list", "post": "create"},
            name="{basename}-character",
            detail=False,
            initkwargs={"suffix": "Character"},
        ),
    ]


router = CustomRouter()
router.register("images", ImageViewSet)
urlpatterns = router.urls
