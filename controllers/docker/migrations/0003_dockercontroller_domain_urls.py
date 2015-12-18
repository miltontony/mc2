# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docker', '0002_dockercontroller_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockercontroller',
            name='domain_urls',
            field=models.URLField(default=b'', max_length=8000),
        ),
    ]
