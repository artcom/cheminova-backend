import logging
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from wagtail.images import get_image_model

logger = logging.getLogger(__name__)

IMAGE_DIRS = ("original_images", "images")


class Command(BaseCommand):
    help = (
        "Removes media files under MEDIA_ROOT that are not referenced in the database."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List files that would be removed without actually deleting them.",
        )
        parser.add_argument(
            "--media-root",
            type=str,
            default=None,
            help="Override the media root directory (default: settings.MEDIA_ROOT).",
        )

    def handle(self, *args, **options) -> None:
        dry_run: bool = options["dry_run"]
        media_root = Path(options["media_root"] or settings.MEDIA_ROOT)

        if not media_root.is_dir():
            self.stderr.write(f"Media root does not exist: {media_root}")
            return

        ImageModel = get_image_model()
        RenditionModel = ImageModel.get_rendition_model()

        referenced: set[Path] = set()
        self.stdout.write("Collecting referenced media files from the database.")
        for name in ImageModel.objects.values_list("file", flat=True):
            if name:
                referenced.add(media_root / name)
            self.stdout.write(f"referenced image: {name}")
        for name in RenditionModel.objects.values_list("file", flat=True):
            if name:
                referenced.add(media_root / name)
            self.stdout.write(f"referenced rendition: {name}")

        removed = 0
        for image_dir_name in IMAGE_DIRS:
            image_dir = media_root / image_dir_name
            if not image_dir.is_dir():
                continue
            for file_path in image_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                if file_path not in referenced:
                    if dry_run:
                        self.stdout.write(f"[dry-run] Would remove: {file_path}")
                    else:
                        file_path.unlink()
                        self.stdout.write(f"Removed unreferenced asset: {file_path}")
                    removed += 1

        action = "Would remove" if dry_run else "Removed"
        self.stdout.write(
            self.style.SUCCESS(f"{action} {removed} unreferenced file(s).")
        )
