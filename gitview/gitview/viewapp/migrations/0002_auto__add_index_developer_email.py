# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Developer', fields ['email']
        db.create_index(u'viewapp_developer', ['email'])


    def backwards(self, orm):
        # Removing index on 'Developer', fields ['email']
        db.delete_index(u'viewapp_developer', ['email'])


    models = {
        u'viewapp.branch': {
            'Meta': {'object_name': 'Branch'},
            'developers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['viewapp.Developer']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_commit': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'latest_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'branches'", 'to': u"orm['viewapp.Project']"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'total_lines': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_lines_deleted': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_lines_inserted': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_patches': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'viewapp.developer': {
            'Meta': {'object_name': 'Developer'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kerb_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'latest_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'patches_amount': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'projects_amount': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_lines': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_lines_deleted': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'total_lines_inserted': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'work_type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        u'viewapp.patch': {
            'Meta': {'object_name': 'Patch'},
            'branch': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'patches'", 'to': u"orm['viewapp.Branch']"}),
            'classification': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'commit_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'developer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'patches'", 'to': u"orm['viewapp.Developer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lines_deleted': ('django.db.models.fields.IntegerField', [], {}),
            'lines_inserted': ('django.db.models.fields.IntegerField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'patches'", 'to': u"orm['viewapp.Project']"}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {}),
            'total_files': ('django.db.models.fields.IntegerField', [], {}),
            'total_lines': ('django.db.models.fields.IntegerField', [], {})
        },
        u'viewapp.project': {
            'Meta': {'object_name': 'Project'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'developers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['viewapp.Developer']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'viewapp.viewapplog': {
            'Meta': {'object_name': 'ViewappLog'},
            'error_comment': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['viewapp']