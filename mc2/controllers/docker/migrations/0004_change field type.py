# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docker', '0003_dockercontroller_domain_urls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dockercontroller',
            name='domain_urls',
            field=models.TextField(default=b'', max_length=8000),
        ),
    ]
