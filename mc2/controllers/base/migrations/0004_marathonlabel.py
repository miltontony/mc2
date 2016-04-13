# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_set_default_for_marathon_cmd'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarathonLabel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('value', models.TextField(null=True, blank=True)),
                ('controller', models.ForeignKey(related_name='label_variables', to='base.Controller')),
            ],
        ),
    ]
