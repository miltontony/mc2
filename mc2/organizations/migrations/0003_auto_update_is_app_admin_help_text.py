# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_organizationuserrelation_is_app_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationuserrelation',
            name='is_app_admin',
            field=models.BooleanField(default=False, help_text='This allows the user to be the organization app administrator and manage its users.'),
        ),
    ]
