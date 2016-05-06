# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_controller_webhook_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='controller',
            name='description',
            field=models.TextField(default=b'', help_text=b'A description to provide more info about a controller', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='controller',
            name='marathon_cmd',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
