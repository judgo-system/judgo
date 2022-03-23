from django.db import models
from web.settings import AUTH_USER_MODEL as User

class Session(models.Model):

    name = models.CharField(blank=True, max_length=255)

    username = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True,
                                      editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    