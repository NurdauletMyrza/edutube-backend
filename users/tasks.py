import logging
from celery import shared_task
from datetime import datetime, timedelta
from .models import User

logger = logging.getLogger(__name__)


@shared_task
def delete_deactivated_users():
    """
    Deletes users who requested deactivation but didn't log in for 30 days.
    """
    threshold_date = datetime.now() - timedelta(days=30)

    users_to_delete = User.objects.filter(
        deactivation_requested=True,
        deactivation_date__lte=threshold_date
    )

    deleted_users = []
    for user in users_to_delete:
        try:
            logger.info(f"Deleting user {user.email}...")
            user.delete()
            deleted_users.append(user.email)
        except Exception as e:
            logger.error(f"Failed to delete user {user.email}: {str(e)}")

    logger.info(f"{len(deleted_users)} users deleted successfully.")
    return f"Deleted users: {', '.join(deleted_users) if deleted_users else 'No users deleted.'}"
