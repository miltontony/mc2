# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docker', '0002_dockercontroller_port'),
    ]

    operations = [
        migrations.CreateModel(
            name='FreeBasicsController',
            fields=[
                ('dockercontroller_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='docker.DockerController')),
                ('selected_template', models.CharField(default=b'molo-tuneme', max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=('docker.dockercontroller',),
        ),
    ]
