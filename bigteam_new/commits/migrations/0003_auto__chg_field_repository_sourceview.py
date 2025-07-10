# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Repository.sourceview'
        db.alter_column('commits_repository', 'sourceview', self.gf('django.db.models.fields.CharField')(max_length=500, null=True))


    def backwards(self, orm):
        
        # Changing field 'Repository.sourceview'
        db.alter_column('commits_repository', 'sourceview', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))


    models = {
        'commits.author': {
            'Meta': {'object_name': 'Author'},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'display': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'commits.commitlog': {
            'Meta': {'object_name': 'CommitLog'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commits'", 'to': "orm['commits.Author']"}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repository': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commits'", 'to': "orm['commits.Repository']"}),
            'revision': ('django.db.models.fields.IntegerField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'commits.repository': {
            'Meta': {'object_name': 'Repository'},
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sourceview': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['commits']
