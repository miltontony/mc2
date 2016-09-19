# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20160907_1857'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(blank=True)),
                ('link', models.TextField(null=True, blank=True)),
                ('controller', models.ForeignKey(related_name='additional_link', to='base.Controller')),
            ],
        ),
    ]
