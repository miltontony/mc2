# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):
        self.create_known_application_types(orm)
        self.copy_app_type_to_application_type(orm)

    def backwards(self, orm):
        self.copy_application_type_to_app_type(orm)

    def create_known_application_types(self, orm):
        FFL = 'ffl'
        GEM = 'gem'
        EBOLA = 'ebola'
        MAMA = 'mama'
        MNM = 'mnm'
        STRAIGHT_TALK = 'straighttalk'
        BAREFOOT_LAW = 'barefootlaw'
        U_REPORT = 'ureport'
        MARIE_STOPES = 'mariestopes'
        FFL_ANGOLA = 'fflangola'
        APONJON = 'aponjon'
        GEM_RWANDA = 'gemrwanda'
        CREA = 'crea'
        EPIC_QUEEN = 'epicqueen'
        CONNECT_SMART = 'connectsmart'
        MY_RIGHTS = 'myrights'

        APP_TYPES = (
            (FFL, 'Facts for Life'),
            (GEM, 'Girl Effect Mobile'),
            (EBOLA, 'Ebola Information'),
            (MAMA, 'MAMA Baby Center'),
            (MNM, 'Malaria no More'),
            (STRAIGHT_TALK, 'Straight Talk'),
            (BAREFOOT_LAW, 'Barefoot Law'),
            (U_REPORT, 'U-Report'),
            (MARIE_STOPES, 'Marie Stopes'),
            (FFL_ANGOLA, 'FFL Angola'),
            (APONJON, 'MAMA Aponjon'),
            (GEM_RWANDA, 'GEM Rwanda'),
            (CREA, 'Crea'),
            (EPIC_QUEEN, 'Epic Queen'),
            (CONNECT_SMART, 'Connect Smart'),
            (MY_RIGHTS, 'My Rights'),
        )

        AppType = orm['unicoremc.AppType']
        for name, title in dict(APP_TYPES).items():
            if not AppType.objects.filter(name=name).exists():
                AppType.objects.create(name=name, title=title)

    def copy_app_type_to_application_type(self, orm):
        Project = orm['unicoremc.Project']
        AppType = orm['unicoremc.AppType']

        for obj in Project.objects.all():
            if not obj.app_type:
                continue

            application_type = AppType.objects.get(name=obj.app_type)
            obj.application_type = application_type
            obj.save()

    def copy_application_type_to_app_type(self, orm):
        Project = orm['unicoremc.Project']

        for obj in Project.objects.all():
            if not obj.app_type:
                continue

            obj.app_type = obj.application_type.name
            obj.save()

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
            'Meta': {'object_name': 'AppType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'unicoremc.localisation': {
            'Meta': {'ordering': "('language_code',)", 'object_name': 'Localisation'},
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        u'unicoremc.project': {
            'Meta': {'ordering': "('app_type', 'country')", 'object_name': 'Project'},
            'app_type': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'application_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['unicoremc.AppType']", 'null': 'True', 'blank': 'True'}),
            'available_languages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['unicoremc.Localisation']", 'null': 'True', 'blank': 'True'}),
            'base_repo_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'cms_custom_domain': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'default_language': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'default_language'", 'null': 'True', 'to': u"orm['unicoremc.Localisation']"}),
            'frontend_custom_domain': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'ga_account_id': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ga_profile_id': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hub_app_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'project_type': ('django.db.models.fields.CharField', [], {'default': "'unicore-cms'", 'max_length': '256'}),
            'project_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'repo_git_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'repo_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'initial'", 'max_length': '50'}),
            'team_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['unicoremc']
    symmetrical = True
