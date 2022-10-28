from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from interfaces import add_log
# import logging

# logger = logging.getLogger(__name__)

@receiver(user_logged_out)
def post_logout(user, **kwargs):
    # logger.info(f"User = '{user.username}' logged out")
    add_log.add_log_entry(user, f"The user = '{user.username}' logged out")