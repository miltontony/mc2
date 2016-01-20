# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnvVariable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.TextField(null=True, blank=True)),
                ('value', models.TextField(null=True, blank=True)),
                ('controller', models.ForeignKey(related_name='env_variables', to='base.Controller')),
            ],
        ),
    ]
