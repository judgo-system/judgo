from judgment.models import Logs

def add_log_entry(user, message):
    log_entry = Logs.objects.create(
        user = user,
        username = user.username,
        log_message = message
    )
    log_entry.save()