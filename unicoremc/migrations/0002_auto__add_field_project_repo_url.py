# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Project.repo_url'
        db.add_column(u'unicoremc_project', 'repo_url',
                      self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Project.repo_url'
        db.delete_column(u'unicoremc_project', 'repo_url')


    models = {
        u'unicoremc.project': {
            'Meta': {'object_name': 'Project'},
            'app_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'base_repo_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repo_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'initial'", 'max_length': '50'})
        }
    }

    complete_apps = ['unicoremc']