# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_auto_update_is_app_admin_help_text'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organization',
            options={'ordering': ('name',)},
        ),
    ]
