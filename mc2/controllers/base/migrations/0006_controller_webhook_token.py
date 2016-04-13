# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_field_defaults'),
    ]

    operations = [
        migrations.AddField(
            model_name='controller',
            name='webhook_token',
            field=models.UUIDField(null=True),
        ),
    ]
