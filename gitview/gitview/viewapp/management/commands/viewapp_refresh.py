# -*- coding: utf-8 -*-

import os
import re
import subprocess
import time

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from viewapp import projectanalyze
from viewapp import views
from viewapp.models import Branch
from viewapp.models import Developer
from viewapp.models import Patch
from viewapp.models import Project
from viewapp.models import Project


class Command(BaseCommand):
    "refresh the data of projects"
    option_list = BaseCommand.option_list + (
        make_option('--all',
                    action='store_true',
                    dest='all',
                    default=False,
                    help="refresh data of all projects"),
        make_option('--addall',
                    action='store_true',
                    dest='addall',
                    default=False,
                    help="refresh data of new projects"),)

    def handle(self, *args, **options):
        project_list = []
        if not args:
            if options['all']:
                project_list = Project.objects.all()
                if options['addall']:
                    project_list = []
                    project_list = Project.objects.filter(name='')
            else:
                if options['addall']:
                    project_list = Project.objects.filter(name='')
        else:
            for name in args:
                try:
                    project = Project.objects.get(name=name)
                    project_list.append(project)
                    print "Added '%s' to refresh queue " % name
                except ObjectDoesNotExist:
                    print "project '%s' not found!" % name
        if not project_list:
            print "No project in refresh queue!"
        else:
            self.refresh(project_list)

    def refresh(self, project_list):
        print time.strftime('\n%Y-%m-%d-%H:%M:%S\nRefreshing data...\n',
                            time.localtime(time.time()))
        for project in project_list:
            try:
                url = project.url
                tmp_str = url.split('/')[-1]
                project_name = tmp_str.replace('.git', '')
                project.name = project_name
                project.save()
                project_dir = os.path.join(settings.PROJECT_DIR, project_name)
                branches = []
                if os.path.exists(project_dir):
                    branches = self.get_branches(project_dir)
                else:
                    os.chdir(settings.PROJECT_DIR)
                    cmd = ' '.join(['git clone -q ', url])
                    try:
                        os.system(cmd)
                    except Exception, error:
                        print error
                    branches = self.get_branches(project_dir)
                try:
                    for name in branches:
                        try:
                            branch = Branch.objects.get(project=project,
                                                        name=name)
                        except ObjectDoesNotExist:
                            branch = Branch(name=name, project=project)
                            branch.save()
                        projectanalyze.run(project, branch)
                except Exception, error:
                    print error
                print time.strftime('\n%Y-%m-%d-%H:%M:%S',
                                    time.localtime(time.time()))
                print "Project '%s' refresh successfully!\n" % project_name
            except Exception, error:
                print error
                print time.strftime('\n%Y-%m-%d-%H:%M:%S',
                                    time.localtime(time.time()))
                print "Project '%s' refresh faild!\n" % project_name

    def get_branches(self, project_dir):
        try:
            os.chdir(project_dir)
        except Exception, error:
            print error
        branch_list = []
        branches = []
        tmp_str = ''
        try:
            cmd_git_remote = 'git remote show origin'
            proc = subprocess.Popen(cmd_git_remote.split(),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            tmp_str = stdout.split('Local branches configured')[0]
            try:
                tmp_str = tmp_str.split('Remote branches:\n')[1]
            except:
                tmp_str = tmp_str.split('Remote branch:\n')[1]
            branches = tmp_str.split('\n')
            for branch in branches[0:-1]:
                if re.search(' tracked', branch) is not None:
                    branch = branch.replace('tracked', '').strip(' ')
                    branch_list.append(branch)
        except Exception, error:
            if branch_list == []:
                print "Can not get any branch!"
        return branch_list
