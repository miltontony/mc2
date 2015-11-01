# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationUserRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_admin', models.BooleanField(default=False, help_text='This allows the user to manage the organization and its users.')),
                ('groups', models.ManyToManyField(to='auth.Group', blank=True)),
                ('organization', models.ForeignKey(to='organizations.Organization')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(to='auth.Permission', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='organization',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='organizations.OrganizationUserRelation'),
        ),
        migrations.AlterUniqueTogether(
            name='organizationuserrelation',
            unique_together=set([('organization', 'user')]),
        ),
    ]
