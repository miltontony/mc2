# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_marathonlabel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='envvariable',
            name='key',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='marathonlabel',
            name='name',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
    ]
