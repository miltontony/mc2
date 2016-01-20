# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docker', '0004_change field type'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockercontroller',
            name='volume_needed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='dockercontroller',
            name='volume_path',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
