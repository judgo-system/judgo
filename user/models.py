from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# from core.models import Session
from judgment.models import Judgment

class User(AbstractUser):

    name = models.CharField(_('Name of User'), blank=True, max_length=255)

    is_reviewer = models.BooleanField(default=False)
    
    latest_judgment = models.OneToOneField(
        Judgment, blank=True, 
        null=True, on_delete=models.SET_NULL,
        related_name="+"
    )

    last_active_time = models.DateTimeField(auto_now_add=True)
    

    last_active_time = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def save(self, *args, **kwargs):
        self.last_active_time = datetime.now()
        super().save(*args, **kwargs)


