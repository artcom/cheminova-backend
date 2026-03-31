from django.core.management.base import BaseCommand
from wagtail.models import ModelLogEntry, PageLogEntry


class Command(BaseCommand):
    help = "Removes all Wagtail edit history (PageLogEntry and ModelLogEntry) from the database."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many records would be deleted without actually deleting them.",
        )

    def handle(self, *args, **options) -> None:
        dry_run: bool = options["dry_run"]

        page_count = PageLogEntry.objects.count()
        model_count = ModelLogEntry.objects.count()
        total = page_count + model_count

        if dry_run:
            self.stdout.write(
                f"[dry-run] Would delete {page_count} PageLogEntry and "
                f"{model_count} ModelLogEntry record(s) ({total} total)."
            )
            return

        PageLogEntry.objects.all().delete()
        ModelLogEntry.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {page_count} PageLogEntry and "
                f"{model_count} ModelLogEntry record(s) ({total} total)."
            )
        )
