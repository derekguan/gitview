# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Developer'
        db.create_table(u'viewapp_developer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kerb_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('patches_amount', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('projects_amount', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('total_lines', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('total_lines_inserted', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('total_lines_deleted', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('latest_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('work_type', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
        ))
        db.send_create_signal(u'viewapp', ['Developer'])

        # Adding model 'Project'
        db.create_table(u'viewapp_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
        ))
        db.send_create_signal(u'viewapp', ['Project'])

        # Adding M2M table for field developers on 'Project'
        m2m_table_name = db.shorten_name(u'viewapp_project_developers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm[u'viewapp.project'], null=False)),
            ('developer', models.ForeignKey(orm[u'viewapp.developer'], null=False))
        ))
        db.create_unique(m2m_table_name, ['project_id', 'developer_id'])

        # Adding model 'Branch'
        db.create_table(u'viewapp_branch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('latest_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('latest_commit', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('total_patches', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('total_lines', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('total_lines_inserted', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('total_lines_deleted', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='branches', to=orm['viewapp.Project'])),
        ))
        db.send_create_signal(u'viewapp', ['Branch'])

        # Adding M2M table for field developers on 'Branch'
        m2m_table_name = db.shorten_name(u'viewapp_branch_developers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('branch', models.ForeignKey(orm[u'viewapp.branch'], null=False)),
            ('developer', models.ForeignKey(orm[u'viewapp.developer'], null=False))
        ))
        db.create_unique(m2m_table_name, ['branch_id', 'developer_id'])

        # Adding model 'Patch'
        db.create_table(u'viewapp_patch', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('commit_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('submit_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('classification', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('total_files', self.gf('django.db.models.fields.IntegerField')()),
            ('lines_inserted', self.gf('django.db.models.fields.IntegerField')()),
            ('lines_deleted', self.gf('django.db.models.fields.IntegerField')()),
            ('total_lines', self.gf('django.db.models.fields.IntegerField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='patches', to=orm['viewapp.Project'])),
            ('branch', self.gf('django.db.models.fields.related.ForeignKey')(related_name='patches', to=orm['viewapp.Branch'])),
            ('developer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='patches', to=orm['viewapp.Developer'])),
        ))
        db.send_create_signal(u'viewapp', ['Patch'])

        # Adding model 'ViewappLog'
        db.create_table(u'viewapp_viewapplog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time_stamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('error_comment', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'viewapp', ['ViewappLog'])


    def backwards(self, orm):
        # Deleting model 'Developer'
        db.delete_table(u'viewapp_developer')

        # Deleting model 'Project'
        db.delete_table(u'viewapp_project')

        # Removing M2M table for field developers on 'Project'
        db.delete_table(db.shorten_name(u'viewapp_project_developers'))

        # Deleting model 'Branch'
        db.delete_table(u'viewapp_branch')

        # Removing M2M table for field developers on 'Branch'
        db.delete_table(db.shorten_name(u'viewapp_branch_developers'))

        # Deleting model 'Patch'
        db.delete_table(u'viewapp_patch')

        # Deleting model 'ViewappLog'
        db.delete_table(u'viewapp_viewapplog')


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
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
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