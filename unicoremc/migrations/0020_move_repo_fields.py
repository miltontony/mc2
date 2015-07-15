# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        for project in orm.Project.objects.all():
            orm.ProjectRepo.objects.create(
                project=project,
                base_url=project.base_repo_url,
                url=project.repo_url,
                git_url=project.repo_git_url)

    def backwards(self, orm):
        "Write your backwards methods here."
        for project in orm.Project.objects.all():
            try:
                repo = project.repo
                project.base_repo_url = repo.base_url
                project.repo_url = repo.url
                project.repo_git_url = repo.git_url
                project.save()
            except ValueError:
                continue

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'unicoremc.apptype': {
            'Meta': {'ordering': "('title',)", 'object_name': 'AppType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'project_type': ('django.db.models.fields.CharField', [], {'default': "'unicore-cms'", 'max_length': '256'}),
            'title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'unicoremc.localisation': {
            'Meta': {'ordering': "('language_code',)", 'object_name': 'Localisation'},
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        u'unicoremc.project': {
            'Meta': {'ordering': "('application_type__title', 'country')", 'object_name': 'Project'},
            'application_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['unicoremc.AppType']", 'null': 'True', 'blank': 'True'}),
            'available_languages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['unicoremc.Localisation']", 'null': 'True', 'blank': 'True'}),
            'base_repo_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'cms_custom_domain': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'default_language': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'default_language'", 'null': 'True', 'to': u"orm['unicoremc.Localisation']"}),
            'external_repos': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'external_projects'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['unicoremc.ProjectRepo']"}),
            'frontend_custom_domain': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'ga_account_id': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ga_profile_id': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hub_app_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'project_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'repo_git_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'repo_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'initial'", 'max_length': '50'}),
            'team_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'unicoremc.projectrepo': {
            'Meta': {'object_name': 'ProjectRepo'},
            'base_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'git_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'repo'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['unicoremc.Project']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['unicoremc']
    symmetrical = True
