# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'unicoremc_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('app_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('base_repo_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('state', self.gf('django.db.models.fields.CharField')(default='initial', max_length=50)),
        ))
        db.send_create_signal(u'unicoremc', ['Project'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table(u'unicoremc_project')


    models = {
        u'unicoremc.project': {
            'Meta': {'object_name': 'Project'},
            'app_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'base_repo_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'initial'", 'max_length': '50'})
        }
    }

    complete_apps = ['unicoremc']