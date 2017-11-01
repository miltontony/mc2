# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_additionallink'),
    ]

    operations = [
        migrations.AddField(
            model_name='controller',
            name='rabbitmq_vhost_host',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='controller',
            name='rabbitmq_vhost_name',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='controller',
            name='rabbitmq_vhost_needed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='controller',
            name='rabbitmq_vhost_password',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='controller',
            name='rabbitmq_vhost_username',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
