import json
from logging import getLogger
from pathlib import Path

from django.contrib.auth.models import User

logger = getLogger(__name__)


def dump_users(output_dir: Path, file_name: str):
    users = (
        User.objects.all()
        .prefetch_related("groups")
        .values(
            "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "is_superuser",
        )
    )

    users_list = [
        {
            **user,
            "groups": list(
                User.objects.get(pk=user["id"]).groups.values_list("name", flat=True)
            ),
        }
        for user in users
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    users_file = output_dir.joinpath(file_name)
    users_file.write_text(json.dumps(users_list, indent=4))
    logger.info(f"Dumped {len(users_list)} users to {users_file}")
