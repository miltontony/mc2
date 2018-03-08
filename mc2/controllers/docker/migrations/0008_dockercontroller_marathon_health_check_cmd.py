# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docker', '0007_dockercontroller_external_visibility'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockercontroller',
            name='marathon_health_check_cmd',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
