# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docker', '0005_add_volume_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dockercontroller',
            name='port',
            field=models.PositiveIntegerField(default=0, null=True, blank=True),
        ),
    ]
