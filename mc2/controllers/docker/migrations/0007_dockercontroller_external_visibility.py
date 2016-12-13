# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docker', '0006_auto_20160810_0653'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockercontroller',
            name='external_visibility',
            field=models.BooleanField(default=True),
        ),
    ]
