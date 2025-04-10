from django.db import models
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.models import Page


class CustomImage(AbstractImage):
    public = models.BooleanField(default=False)

    admin_form_fields = Image.admin_form_fields + ("public",)

    def get_referenced_live_pages(self) -> list[Page]:
        """
        Get all referenced live pages that are using this image.
        """
        return [
            reference_index[0] for reference_index in self.get_usage()
            if isinstance(reference_index[0], Page)
            and reference_index[0].live
        ]


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name="renditions")

    class Meta:
        unique_together = (
            ("image", "filter_spec", "focal_point_key"),
        )
