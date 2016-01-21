# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_envvariable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controller',
            name='marathon_cmd',
            field=models.TextField(default=b''),
        ),
    ]
