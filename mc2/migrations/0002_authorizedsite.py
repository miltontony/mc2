# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('mc2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorizedSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site', models.CharField(max_length=200)),
                ('group', models.ManyToManyField(to='auth.Group')),
            ],
        ),
    ]
