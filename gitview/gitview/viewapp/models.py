# -*- coding: utf-8 -*-

from django.db import models


# FIXME: reuse django.contrib.auth.User
class Developer(models.Model):
    kerb_name = models.CharField(max_length=100)
    patches_amount = models.IntegerField(blank=True, null=True)
    projects_amount = models.IntegerField(blank=True, null=True)
    total_lines = models.IntegerField(blank=True, null=True)
    total_lines_inserted = models.IntegerField(blank=True, null=True)
    total_lines_deleted = models.IntegerField(blank=True, null=True)
    latest_update = models.DateTimeField(blank=True, null=True)
    work_type = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField(unique=True, db_index=True)

    def __unicode__(self):
        return self.kerb_name


class Project(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(unique=True,
                          help_text='Gitview clones project to fetch '
                                    'statistics only, so the URL allowing '
                                    'anonymous access is enough.')
    developers = models.ManyToManyField(Developer, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Branch(models.Model):
    """to support Branch"""
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField(blank=True, null=True)
    latest_update = models.DateTimeField(blank=True, null=True)
    latest_commit = models.CharField(max_length=15, blank=True, null=True)
    total_patches = models.IntegerField(blank=True, null=True)
    #total_files = models.IntegerField(blank=True, null=True)
    total_lines = models.IntegerField(blank=True, null=True)
    total_lines_inserted = models.IntegerField(blank=True, null=True)
    total_lines_deleted = models.IntegerField(blank=True, null=True)
    developers = models.ManyToManyField(Developer, blank=True, null=True)
    project = models.ForeignKey(Project, related_name='branches')

    def __unicode__(self):
        return '%s %s' % (self.project.name, self.name)


class Patch(models.Model):
    commit_id = models.CharField(max_length=50)
    #patch_message = models.CharField(max_length=500)
    submit_date = models.DateTimeField()
    classification = models.CharField(max_length=4)
    total_files = models.IntegerField()
    lines_inserted = models.IntegerField()
    lines_deleted = models.IntegerField()
    total_lines = models.IntegerField()
    project = models.ForeignKey(Project, related_name='patches')
    branch = models.ForeignKey(Branch, related_name='patches')
    developer = models.ForeignKey(Developer, related_name='patches')

    def __unicode__(self):
        return '%s %s %s' % (self.project.name,
                             self.branch.name,
                             self.commit_id)


class ViewappLog(models.Model):
    """viewapp_error_log"""
    time_stamp = models.DateTimeField()
    error_comment = models.CharField(max_length=300)

    def __unicode__(self):
        return self.error_comment
