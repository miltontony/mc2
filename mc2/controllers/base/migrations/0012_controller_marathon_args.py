# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_add_on_delete_to_controller_foreignkey'),
    ]

    operations = [
        migrations.AddField(
            model_name='controller',
            name='marathon_args',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
    ]
