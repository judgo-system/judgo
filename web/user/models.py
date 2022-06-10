from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.models import Session
from judgment.models import Judgment

class User(AbstractUser):

    name = models.CharField(_('Name of User'), blank=True, max_length=255)

    active_session = models.ForeignKey(
        Session, blank=True, 
        null=True, on_delete=models.SET_NULL
    )
    
    latest_judgment = models.OneToOneField(
        Judgment, blank=True, 
        null=True, on_delete=models.SET_NULL,
        related_name="+"
    )

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})
