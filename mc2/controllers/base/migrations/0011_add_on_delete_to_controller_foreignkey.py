# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_add_rabbitmq_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controller',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='organizations.Organization', null=True),
        ),
        migrations.AlterField(
            model_name='controller',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
