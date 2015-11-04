# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='controller',
            name='class_name',
            field=models.CharField(max_length=255, null=True, editable=False),
        ),
    ]
