# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_controller_health_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controller',
            name='health_status',
            field=models.TextField(default=b'{"message": "No health status available", "error": true}'),
        ),
    ]
