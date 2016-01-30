# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docker', '0005_add_volume_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockercontroller',
            name='volume_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
