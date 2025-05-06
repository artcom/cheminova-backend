from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from image_upload import urls as image_upload_urls
from image_auth import urls as image_auth_urls
from rest_framework.routers import DefaultRouter
from rest_framework import urls as rest_framework_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from experience.views import (
    WelcomeViewSet,
    CharacterOverviewViewSet,
    ChooseCharacterViewSet,
)
from custom_images.views import CustomImageViewSet

router = DefaultRouter()
router.register(r"api/welcome", WelcomeViewSet, basename="welcome")
router.register(
    r"api/character-overview", CharacterOverviewViewSet, basename="character-overview"
)
router.register(
    r"api/choose-character", ChooseCharacterViewSet, basename="choose-character"
)
router.register(r"api/images", CustomImageViewSet, basename="images")

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("api/upload/", include(image_upload_urls)),
    path("api/image-auth/", include(image_auth_urls)),
    path("api-auth/", include(rest_framework_urls, namespace="rest_framework")),
]

urlpatterns = urlpatterns + router.urls

if settings.DEBUG and settings.SERVE_STATIC:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
