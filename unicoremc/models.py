from django.db import models
from django.contrib.auth.models import User


class UserSettings(models.Model):
    BASIC_SETTINGS_LEVEL = 'basic'
    ADVANCED_SETTINGS_LEVEL = 'advanced'
    EXPERT_SETTINGS_LEVEL = 'expert'
    SETTINGS_LEVEL_CHOICES = (
        (BASIC_SETTINGS_LEVEL, 'Basic'),
        (ADVANCED_SETTINGS_LEVEL, 'Advanced'),
        (EXPERT_SETTINGS_LEVEL, 'Expert'),
    )
    user = models.OneToOneField(
        User, related_name="settings", primary_key=True)
    settings_level = models.CharField(
        max_length=100,
        choices=SETTINGS_LEVEL_CHOICES,
        default=BASIC_SETTINGS_LEVEL)
