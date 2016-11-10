# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationuserrelation',
            name='is_app_admin',
            field=models.BooleanField(default=False, help_text='This allows the user to be their apps administrator and manage their apps users.'),
        ),
    ]
