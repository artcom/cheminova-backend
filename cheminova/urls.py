from caseutil import to_kebab
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework import urls as rest_framework_urls
from rest_framework.routers import DefaultRouter
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

import experience.models
import experience.views
from image_auth import urls as image_auth_urls
from image_upload import urls as image_upload_urls

router = DefaultRouter()
for model in experience.models.__all__:
    endpoint = to_kebab(model)
    router.register(
        endpoint,
        getattr(experience.views, f"{model}ViewSet"),
    )


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("api/", include(router.urls)),
    path("api/image-auth/", include(image_auth_urls)),
    path("api/upload/", include(image_upload_urls)),
    path("api-auth/", include(rest_framework_urls, namespace="rest_framework")),
]


if settings.DEBUG and settings.SERVE_STATIC:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
