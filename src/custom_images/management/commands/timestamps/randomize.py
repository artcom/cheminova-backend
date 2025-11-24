import random
from datetime import timedelta
from logging import getLogger

from django.utils import timezone
from wagtail.images import get_image_model

from experience.models import Character

logger = getLogger(__name__)


def randomize_timestamps(character: str, n_days: int = 30) -> None:
    ImageModel = get_image_model()

    if character:
        approved_collections = (
            Character.objects.filter(slug=character)
            .values_list("approved_collection_id", flat=True)
            .distinct()
        )
    else:
        approved_collections = (
            Character.objects.all()
            .values_list("approved_collection_id", flat=True)
            .distinct()
        )

    images_to_randomize = ImageModel.objects.filter(
        collection_id__in=list(approved_collections)
    )

    now = timezone.now()

    for image in images_to_randomize:
        random_seconds = random.randint(0, n_days * 24 * 60 * 60)
        random_datetime = now - timedelta(seconds=random_seconds)
        image.created_at = random_datetime
        image.save()

    logger.info(f"Randomized timestamps for {images_to_randomize.count()} images.")
