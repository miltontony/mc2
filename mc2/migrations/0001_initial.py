# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('user', models.OneToOneField(related_name='settings', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('settings_level', models.CharField(default=b'basic', max_length=100, choices=[(b'basic', b'Basic'), (b'advanced', b'Advanced'), (b'expert', b'Expert')])),
            ],
        ),
    ]
