# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_default_user_settings_for_user(apps, schema_editor):
    User = apps.get_model("auth", "User")  # noqa
    UserSettings = apps.get_model("unicoremc", "UserSettings")  # noqa

    for user in User.objects.all():
        UserSettings.objects.get_or_create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ('unicoremc', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_user_settings_for_user),
    ]
