from django.db import models
from django.contrib.auth import get_user_model


class Organization(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(
        get_user_model(),
        through='OrganizationUserRelation')


class OrganizationUserRelation(models.Model):
    organization = models.ForeignKey(Organization)
    user = models.ForeignKey(get_user_model())
    is_admin = models.BooleanField(default=False)
