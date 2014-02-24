# -*- coding: utf-8 -*-
import datetime
import os
import re
import subprocess
import sys
import threading

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from viewapp.models import Branch
from viewapp.models import Developer
from viewapp.models import Patch
from viewapp.models import Project
from viewapp.models import ViewappLog

threading._DummyThread._Thread__stop = lambda x: 42


#  commit classfication distinguish by commit message
CLASSIFICATION = ['REV', 'SQL', 'FIX', 'DOC']


#collect data of project when first load
class ProjectDataCollect():
    project_name = ""
    start_date = datetime.datetime.fromtimestamp(float(0))
    latest_update = datetime.datetime.fromtimestamp(float(0))
    latest_commit = 0
    total_patches = 0
    total_lines = 0
    total_lines_inserted = 0
    total_lines_deleted = 0
    author_dictionary = {}
    commit_dictionary = {}
    commit_begin = ''
    commit_end = ''
    current_commit = None

    def collect(self, project, branch):
        """Collect branch data to refresh DB.

        Analyzing git log of branch will be done to
        collect commits data for DB

        Args:
            project: An object of DB table viewapp_project
            branch: A branch Object of project
        """
        # reset class variable
        self.clear_data()
        # sync branch info
        self.branch_data_sync(project, branch)
        if self.commit_begin is '':
            # log period need to be concerned
            # if branch has never been dealt with
            period = 'HEAD'
        else:
            period = '...'.join([self.commit_begin, self.commit_end])
        project_dir = os.path.join(settings.PROJECT_DIR, project.name)
        try:
            os.chdir(project_dir)
            os.system('git checkout -q ' + branch.name)
            try:
                os.system('git pull -q ')
            except Exception, error:
                print error
            # git log command for no merges commits
            cmd_git_log = ["git", "log", "--shortstat", "--no-merges", "-m",
                           "--pretty=format:%h %at %aN <%aE> %s", period]
            proc = subprocess.Popen(cmd_git_log,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            self.deal_lines(stdout.split('\n'), 'no_merges')
            # git log command for merges commits
            cmd_git_log = ["git", "log", "--shortstat", "--first-parent",
                           "--merges", "-m",
                           "--pretty=format:%h %at %aN <%aE> %s", period]
            proc = subprocess.Popen(cmd_git_log,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            self.deal_lines(stdout.split('\n'), 'merges')
            try:
                self.database_operate(project, branch)
            except Exception, error:
                print error
        except Exception, error:
            print error

    def deal_lines(self, lines, conf):
        """Collect detail data of lines list.

        From log lines, this method will extract detail commit message
        including code lines and author information.

        Args:
            lines: log lines collected by collect(self, project, branch).
            conf: merges commits or no merges commits

        Return:
            If there are new commits, detail will be save into
            author_dictionary and commit_dictionary.
        """
        if lines == ['']:
            print "NO new %s commit!" % conf
        else:
            for line in lines:
                if re.search('\d+ files? changed', line) is None:
                    pos = line.find(' ')
                    if pos != -1:
                        try:
                            parts = line.split(' ', 2)
                            commit_id = parts[0]
                            self.current_commit = commit_id
                            stamp = int(parts[1])
                            ti = datetime.datetime.fromtimestamp(float(stamp))
                            s_time = datetime.datetime.fromtimestamp(float(0))
                            if self.start_date == s_time:
                                self.start_date = ti
                            elif self.start_date > ti:
                                self.start_date = ti
                            author, mail = parts[2].split('<', 1)
                            message = mail.split('> ', 1)[1]
                            mail = mail.split('>', 1)[0]
                            if re.search(': ', message) is not None:
                                messagetype = message.split(': ', 1)[0]
                                if messagetype not in CLASSIFICATION:
                                    messagetype = 'OTR'
                            else:
                                messagetype = 'OTR'
                            if commit_id not in self.commit_dictionary:
                                self.commit_dictionary[commit_id]\
                                    = [commit_id, mail,
                                       stamp, messagetype,
                                       messagetype, 0, 0, 0, 0]
                            # [files, inserted, deleted, total_lines]
                            if mail not in self.author_dictionary:
                                self.author_dictionary[mail] = [author,
                                                                mail, 0, 0,
                                                                0, 0, 1,
                                                                stamp]
                            # [files,inserted,deleted,total_lines,commit,stamp]
                            else:
                                self.author_dictionary[mail][6] += 1
                                if stamp > self.author_dictionary[mail][7]:
                                    self.author_dictionary[mail][7] = stamp
                            self.total_patches += 1
                        except:
                            print 'Warning: unexpected line "%s"' % line
                else:
                    if conf == 'no_merges':
                        try:
                            commit_id = self.current_commit
                            numbers = self.getstatsummarycounts(line)
                            if len(numbers) == 3:
                                (files, inserted, deleted) = \
                                    map(lambda el: int(el), numbers)
                            total_lines = inserted - deleted
                            self.commit_dictionary[commit_id][5] = files
                            self.commit_dictionary[commit_id][6] = inserted
                            self.commit_dictionary[commit_id][7] = deleted
                            self.commit_dictionary[commit_id][8] = total_lines
                            self.author_dictionary[mail][2] += files
                            self.author_dictionary[mail][3] += inserted
                            self.author_dictionary[mail][4] += deleted
                            self.author_dictionary[mail][5] += total_lines
                            self.total_lines_inserted += inserted
                            self.total_lines_deleted += deleted
                            self.total_lines += total_lines
                            self.current_commit = None
                        except:
                            print 'Warning: unexpected line "%s"' % line

    def database_operate(self, project, branch):
        """Save data of commits into  DB.

        Collecting and Analyzing are done, this method will save
        the data into server DB.

        Args:
            project: An object of DB table viewapp_project
            branch: A branch Object of project
        """
        # branch data
        try:
            branch.start_date = self.start_date
            branch.latest_update = self.latest_update
            branch.latest_commit = self.latest_commit
            branch.total_patches += self.total_patches
            branch.total_lines += self.total_lines
            branch.total_lines_inserted += self.total_lines_inserted
            branch.total_lines_deleted += self.total_lines_deleted
            branch.save()
            print "Updated branch '%s' for %s" % (branch.name, project.name)
        except:
            print ' '.join(["saved project data failed!", project, branch])
        try:
            # recognize author by mail
            for mail in self.author_dictionary:
                email = self.author_dictionary[mail][1]
                try:
                    developer = Developer.objects.get(email=email)
                    stamp = float(self.author_dictionary[mail][7])
                    developer.patches_amount += \
                        self.author_dictionary[mail][6]
                    developer.total_lines += \
                        self.author_dictionary[mail][5]
                    developer.total_lines_inserted += \
                        self.author_dictionary[mail][3]
                    developer.total_lines_deleted += \
                        self.author_dictionary[mail][4]
                    developer.latest_update = \
                        datetime.datetime.fromtimestamp(stamp)
                    developer.save()
                    try:
                        if developer not in branch.developers.all():
                            branch.developers.add(developer)
                            branch.save()
                        if developer not in project.developers.all():
                            project.developers.add(developer)
                            project.save()
                            developer.projects_amount += 1
                            developer.save()
                    except Exception, error:
                        print error
                except ObjectDoesNotExist:
                    stamp = float(self.author_dictionary[mail][7])
                    print mail
                    kerb_name = self.author_dictionary[mail][0].strip(' ')
                    developer = Developer(
                        kerb_name=kerb_name,
                        patches_amount=self.author_dictionary[mail][6],
                        projects_amount=1,
                        total_lines=self.author_dictionary[mail][5],
                        total_lines_inserted=self.author_dictionary[mail][3],
                        total_lines_deleted=self.author_dictionary[mail][4],
                        latest_update=datetime.datetime.fromtimestamp(stamp),
                        work_type="developer",
                        email=self.author_dictionary[mail][1])
                    developer.save()
                    branch.developers.add(developer)
                    branch.save()
                    project.developers.add(developer)
                    project.save()
            print "Saved data of developers from branch '%s' of %s"\
                  % (branch.name, project.name)
        except Exception, error:
            print error
        # commits data
        try:
            for commit in self.commit_dictionary:
                patch_id = self.commit_dictionary[commit][0]
                try:
                    # deal with double counting
                    patch = Patch.objects.get(commit_id=patch_id,
                                              branch=branch)
                    if patch.submit_date >= branch.latest_update:
                        branch.latest_update = patch.submit_date
                        branch.latest_commit = patch.commit_id
                    branch.total_patches -= 1
                    branch.total_lines -= patch.total_lines
                    branch.total_lines_inserted -= patch.lines_inserted
                    branch.total_lines_deleted -= patch.lines_deleted
                    branch.save()
                    author = patch.developer
                    author.patches_amount -= 1
                    author.total_lines -= patch.total_lines
                    author.total_lines_inserted -= patch.lines_inserted
                    author.total_lines_deleted -= patch.lines_deleted
                    author.save()
                except ObjectDoesNotExist:
                    stamp = float(self.commit_dictionary[commit][2])
                    stamp_time = datetime.datetime.fromtimestamp(stamp)
                    commit_type = self.commit_dictionary[commit][3]
                    files = self.commit_dictionary[commit][5]
                    inserted = self.commit_dictionary[commit][6]
                    deleted = self.commit_dictionary[commit][7]
                    total_lines = self.commit_dictionary[commit][8]
                    patch = Patch(commit_id=self.commit_dictionary[commit][0],
                                  submit_date=stamp_time,
                                  classification=commit_type,
                                  total_files=files,
                                  lines_inserted=inserted,
                                  lines_deleted=deleted,
                                  branch=branch,
                                  project=project,
                                  total_lines=total_lines)
                    author_mail = self.commit_dictionary[commit][1]
                    try:
                        author = Developer.objects.get(email=author_mail)
                        patch.developer = author
                        patch.save()
                        if patch.submit_date > branch.latest_update:
                            branch.latest_update = patch.submit_date
                            branch.latest_commit = patch.commit_id
                            branch.save()
                    except Exception, error:
                        print error
            print "Saved data of commits from the branch '%s' of %s \n"\
                  % (branch.name, project.name)
        except Exception, error:
            print error

    def branch_data_sync(self, project, branch):
        if branch.latest_commit is None:
            branch.latest_commit = ''
        if branch.start_date is None:
            branch.start_date = datetime.datetime.fromtimestamp(float(0))
        if branch.latest_update is None:
            branch.latest_update = datetime.datetime.fromtimestamp(float(0))
        if branch.total_patches is None:
            branch.total_patches = 0
        if branch.total_lines is None:
            branch.total_lines = 0
        if branch.total_lines_inserted is None:
            branch.total_lines_inserted = 0
        if branch.total_lines_deleted is None:
            branch.total_lines_deleted = 0
        branch.save()
        self.project_name = project.name
        self.start_date = branch.start_date
        self.latest_update = branch.latest_update
        self.latest_commit = branch.latest_commit
        self.commit_begin = branch.latest_commit
        self.commit_end = "HEAD"
        if self.commit_begin == '':
            print self.commit_end
        else:
            print ("...").join([self.commit_begin, self.commit_end])

    def getstatsummarycounts(self, line):
        numbers = re.findall('\d+', line)
        if len(numbers) == 1:
            # neither insertions nor deletions:
            # may probably only happen for "0 files changed"
            numbers.append(0)
            numbers.append(0)
        elif len(numbers) == 2 and line.find('(+)') != -1:
            numbers.append(0)     # only insertions were printed on line
        elif len(numbers) == 2 and line.find('(-)') != -1:
            numbers.insert(1, 0)  # only deletions were printed on line
        return numbers

    def clear_data(self):
        self.project_name = ""
        self.start_date = 0
        self.latest_update = 0
        self.latest_commit = 0
        self.total_patches = 0
        self.total_lines = 0
        self.total_lines_inserted = 0
        self.total_lines_deleted = 0
        self.author_dictionary.clear()
        self.commit_dictionary.clear()


def run(project, branch):
    """Refresh commits data of branch.

    This method will be called when gitview refresh data.

    Args:
        project: An object of DB table viewapp_project
        branch: A branch Object of project
    """
    try:
        print ' '.join([project.name, branch.name])
        data = ProjectDataCollect()
        data.collect(project, branch)
    except Exception, error:
        print error
