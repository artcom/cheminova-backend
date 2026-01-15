import json
from logging import getLogger
from pathlib import Path

from django.contrib.auth.models import Group, User

logger = getLogger(__name__)


def restore_users(users_file: Path) -> None:
    if not users_file.exists():
        logger.error(f"Users file {users_file} does not exist.")
        return

    users_data = json.loads(users_file.read_text())
    for user_data in users_data:
        username = user_data["username"]
        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                "email": user_data["email"],
                "is_staff": user_data["is_staff"],
                "is_active": user_data["is_active"],
                "is_superuser": user_data["is_superuser"],
                "password": user_data["password"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
            },
        )

        if user_data["groups"]:
            for group in user_data["groups"]:
                db_group = Group.objects.get(name=group)
                user.groups.add(db_group)

        if created:
            logger.info(f"Created user: {username}")
        else:
            logger.info(f"Updated user: {username}")
