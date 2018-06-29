# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_auto_20170302_0944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controller',
            name='health_status',
            field=models.TextField(default=b'{"message": "No health status available", "error": true}', null=True, blank=True),
        ),
    ]
