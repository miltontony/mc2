# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20160416_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='controller',
            name='postgres_db_host',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='controller',
            name='postgres_db_name',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='controller',
            name='postgres_db_needed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='controller',
            name='postgres_db_password',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='controller',
            name='postgres_db_username',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
