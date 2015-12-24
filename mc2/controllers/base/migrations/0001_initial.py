# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Controller',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('marathon_cpus', models.FloatField(default=0.1)),
                ('marathon_mem', models.FloatField(default=128.0)),
                ('marathon_instances', models.IntegerField(default=1)),
                ('marathon_cmd', models.TextField()),
                ('name', models.TextField(help_text=b'A descriptive name to uniquely identify a controller')),
                ('slug', models.SlugField(help_text=b'Unique name for use in marathon id', max_length=255)),
                ('state', models.CharField(default=b'initial', max_length=50)),
                ('team_id', models.IntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date and time on which this item was created. This isautomatically set on creation', verbose_name='Created Date & Time', db_index=True)),
                ('modified_at', models.DateTimeField(auto_now=True, help_text='Date and time on which this item was last modified. Thisis automatically set each time the item is saved.', verbose_name='Modified Date & Time', db_index=True)),
                ('organization', models.ForeignKey(blank=True, to='organizations.Organization', null=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_base.controller_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]
