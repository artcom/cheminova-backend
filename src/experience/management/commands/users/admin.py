from logging import getLogger

from django.contrib.auth.models import User

logger = getLogger(__name__)


def create_or_update_admin(
    username: str, email: str, first_name: str, last_name: str, password: str
) -> None:
    try:
        admin = User.objects.get(username=username)
        admin.email = email
        admin.first_name = first_name
        admin.last_name = last_name
        admin.set_password(password)
        admin.save()
        logger.info("Updated admin user.")
    except User.DoesNotExist:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        logger.info("Created admin user.")
