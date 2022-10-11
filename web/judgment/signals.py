from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_out)
def post_logout(user, **kwargs):
    logger.info(f"User = '{user.username}' logged out")