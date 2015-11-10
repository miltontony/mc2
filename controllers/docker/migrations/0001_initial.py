# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DockerController',
            fields=[
                ('controller_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base.Controller')),
                ('docker_image', models.CharField(max_length=256)),
                ('marathon_health_check_path', models.CharField(max_length=255, null=True, blank=True)),
            ],
            bases=('base.controller',),
        ),
    ]
