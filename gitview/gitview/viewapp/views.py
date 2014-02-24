# -*- coding: utf-8 -*-

import datetime
import os
import subprocess
import thread
import time

import reportlab.lib.fonts

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas

from viewapp import projectanalyze
from viewapp.models import Branch
from viewapp.models import Developer
from viewapp.models import Patch
from viewapp.models import Project


def index(request):
    """Home Page of gitview, show the list of projects and
    developers.

    Query all objects of projects and developers in DB, and
    show on the page.
    """
    project_list = Project.objects.all()
    author_list = Developer.objects.all()
    return render_to_response("viewapp/index.html", {
        'project_list': project_list,
        'author_list': author_list
    }, context_instance=RequestContext(request))


def project_report(request):
    """Overview of one project.

    List branchs of project, visitor can get general data
    of every branch.
    """
    parts = request.path.split('/')
    project_id = parts[-1]
    project_developers = []
    branches_list = []
    branch_developers = {}
    project = Project.objects.get(id=project_id)
    project_developers = project.developers.all()
    try:
        branches_list = Branch.objects.filter(project=project)
        for branch in branches_list:
            developers = branch.developers.all()
            developers_list = []
            for developer in developers:
                developers_list.append(developer.kerb_name)
            branch_developers[branch.name] = developers_list
        return render_to_response("viewapp/show.html",
                          {'project': project,
                           'project_developers': project_developers,
                           'branches_list': branches_list,
                           'branch_developers': branch_developers},
                          context_instance=RequestContext(request))
    except:
        return render_to_response("viewapp/show.html",
                              {'project': project,
                               'project_developers': project_developers,},
                              context_instance=RequestContext(request))


# search page of branch
def branch_search_show(request):
    time_range = {'year': range(2005, 2020),
                  'month': range(1, 13), 'day': range(1, 32)}
    branch_list = Branch.objects.all()
    return render_to_response("viewapp/branch_search.html",
                              {'time_range': time_range,
                               'branch_list': branch_list},
                              context_instance=RequestContext(request))


# Search branch data as requested
def branch_search_report(request):
    time_range = {'year': range(2005, 2020),
                  'month': range(1, 13), 'day': range(1, 32)}
    branch_all = Branch.objects.all()
    commit_list = []
    commits_data = {'0': 0, '1': 0, '2': 0, '3': 0}
    [date_from, date_to] = get_date_range(request)
    if date_from < date_to:
        if 'branch' in request.GET:
            branch_id = request.GET['branch']
            try:
                branch = Branch.objects.get(id=branch_id)
                project = branch.project
            except Exception, error:
                print error
            try:
                commit_list = Patch.objects.filter(project=project,
                                                   branch=branch,
                                                   submit_date__range=
                                                   (date_from, date_to))
            except Exception, error:
                print error
            if len(commit_list) >= 1:
                commits_data['0'] = len(commit_list)
                for commit in commit_list:
                    commits_data['1'] += commit.lines_inserted
                    commits_data['2'] += commit.lines_deleted
                    commits_data['3'] += commit.total_lines
            return render_to_response("viewapp/branch_search.html",
                                      {'time_range': time_range,
                                       'branch_list': branch_all,
                                       'branch': branch,
                                       'date_from': date_from,
                                       'date_to': date_to,
                                       'commits_data': commits_data,
                                       'commit_list': commit_list},
                                      context_instance=RequestContext(request))
    else:
        return render_to_response("viewapp/branch_search.html",
                                  {'time_range': time_range,
                                   'branch_list': branch_all},
                                  context_instance=RequestContext(request))


# search page of author
def author_search(request):
    parts = request.path.split('/', 3)
    author_id = parts[3].strip('/')
    try:
        author = Developer.objects.get(id=author_id)
    except Exception, error:
        print error
    time_range = {'year': range(2005, 2020),
                  'month': range(1, 13), 'day': range(1, 32)}
    branch_list = author.branch_set.all()
    return render_to_response("viewapp/developer_search.html",
                              {'time_range': time_range,
                               'branch_list': branch_list,
                               'author': author},
                              context_instance=RequestContext(request))


# search author data as requested
def author_search_show(request):
    time_range = {'year': range(2005, 2020),
                  'month': range(1, 13), 'day': range(1, 32)}
    commit_list = []
    commits_data = {'0': 0, '1': 0, '2': 0, '3': 0}
    [date_from, date_to] = get_date_range(request)
    if 'author'in request.GET and 'branch' in request.GET:
        branch_id = request.GET['branch']
        author_id = request.GET['author']
        try:
            author = Developer.objects.get(id=author_id)
            branch_list = author.branch_set.all()
            branch = Branch.objects.get(id=branch_id)
            project = branch.project
        except Exception, error:
            print error
        try:
            commit_list = Patch.objects.filter(project=project,
                                               branch=branch,
                                               developer=author,
                                               submit_date__range=
                                               (date_from, date_to))
            if len(commit_list) >= 1:
                commits_data['0'] = len(commit_list)
                for commit in commit_list:
                    commits_data['1'] += commit.lines_inserted
                    commits_data['2'] += commit.lines_deleted
                    commits_data['3'] += commit.total_lines
            return render_to_response("viewapp/developer_search.html",
                                      {'time_range': time_range,
                                       'branch_list': branch_list,
                                       'author': author,
                                       'date_from': date_from,
                                       'date_to': date_to,
                                       'commits_data': commits_data,
                                       'commit_list': commit_list},
                                      context_instance=RequestContext(request))
        except Exception, error:
            print error
        return render_to_response("viewapp/developer_search.html",
                                  {'time_range': time_range,
                                   'branch_list': branch_list,
                                   'author': author},
                                  context_instance=RequestContext(request))


# interim report page
def interim_report_toweb(request):
    """Iterim report.

    When date given, report of the day, the week and the month before
    the date will be showed.
    """
    time_range = {'year': range(2005, 2020),
                  'month': range(1, 13), 'day': range(1, 32)}
    day_dics = []
    day_projects = []
    day_developers = []
    week_dics = []
    week_projects = []
    week_developers = []
    m_dics = []
    m_projects = []
    m_developers = []
    if 'year' and 'month' and 'day' in request.GET:
        try:
            year = request.GET['year']
            month = request.GET['month']
            day = request.GET['day']
            d = datetime.datetime(int(year), int(month), int(day), 12, 0, 0)
            day_dics = day_report(d)
            day_abstract = interim_dics_abstract(day_dics)
            day_projects = day_abstract[0]
            day_developers = day_abstract[1]
            week_dics = week_report(d)
            week_abstract = interim_dics_abstract(week_dics)
            week_projects = week_abstract[0]
            week_developers = week_abstract[1]
            m_dics = month_report(d)
            m_abstract = interim_dics_abstract(m_dics)
            m_projects = m_abstract[0]
            m_developers = m_abstract[1]
            return render_to_response("viewapp/interim_report.html",
                                      {'time_range': time_range,
                                       'day_from': day_dics[2],
                                       'day_to': day_dics[3],
                                       'day_projects_list': day_projects,
                                       'day_developers_list': day_developers,
                                       'week_from': week_dics[2],
                                       'week_to': week_dics[3],
                                       'week_projects_list': week_projects,
                                       'week_developers_list': week_developers,
                                       'month_from': m_dics[2],
                                       'month_to': m_dics[3],
                                       'month_projects_list': m_projects,
                                       'month_developers_list': m_developers
                                       })
        except Exception, error:
            print error
            return render_to_response("viewapp/interim_report.html",
                                      {'time_range': time_range},
                                      context_instance=RequestContext(request))
    else:
        return render_to_response("viewapp/interim_report.html",
                                  {'time_range': time_range},
                                  context_instance=RequestContext(request))


def team_report(request):
    """Team report.

    This moudule can give PDF report of several projects and developers.
    """
    project_list = Project.objects.all()
    author_list = Developer.objects.all()
    time_range = {'year': range(2005, 2020),
                  'month': range(1, 13), 'day': range(1, 32)}
    [date_from, date_to] = get_date_range(request)
    if date_from < date_to:
        [projects, developers] =\
            report_request_data(request, date_from, date_to)
        return web_report_to_PDF(projects, developers, date_from, date_to)
    else:
        return render_to_response("viewapp/team_report.html",
                                  {'time_range': time_range,
                                   'project_list': project_list,
                                   'author_list': author_list},
                                  context_instance=RequestContext(request))


# For interim report
def interim_dics_abstract(dics):
    projects_list = []
    developers_list = []
    for project_id in dics[0]:
        project = dics[0][project_id][0]
        lines_inserted = dics[0][project_id][1]
        lines_deleted = dics[0][project_id][2]
        total_lines = dics[0][project_id][3]
        commits_amount = dics[0][project_id][4]
        project_list = [project.name, lines_inserted,
                        lines_deleted, total_lines, commits_amount]
        projects_list.append(project_list)
    for developer_id in dics[1]:
        developer = dics[1][developer_id][0]
        lines_inserted = dics[1][developer_id][1]
        lines_deleted = dics[1][developer_id][2]
        total_lines = dics[1][developer_id][3]
        commits_amount = dics[1][developer_id][4]
        developer_list = [developer.kerb_name, developer.email,
                          lines_inserted, lines_deleted,
                          total_lines, commits_amount]
        developers_list.append(developer_list)
    return projects_list, developers_list


# For interim report
def interim_report(date_from, date_to):
    projects_dictionary = {}
    developers_dictionary = {}
    commit_list = Patch.objects.filter(submit_date__range=(date_from,
                                                           date_to))
    for commit in commit_list:
        if commit.project.id not in projects_dictionary:
            projects_dictionary[commit.project.id] = [commit.project,
                                                      commit.lines_inserted,
                                                      commit.lines_deleted,
                                                      commit.total_lines, 1]
        else:
            projects_dictionary[commit.project.id][1] += commit.lines_inserted
            projects_dictionary[commit.project.id][2] += commit.lines_deleted
            projects_dictionary[commit.project.id][3] += commit.total_lines
            projects_dictionary[commit.project.id][4] += 1
        if commit.developer.id not in developers_dictionary:
            developer = [commit.developer,
                         commit.lines_inserted,
                         commit.lines_deleted,
                         commit.total_lines, 1]
            developers_dictionary[commit.developer.id] = developer
        else:
            insert = commit.lines_inserted
            delete = commit.lines_deleted
            total = commit.total_lines
            developers_dictionary[commit.developer.id][1] += insert
            developers_dictionary[commit.developer.id][2] += delete
            developers_dictionary[commit.developer.id][3] += total
            developers_dictionary[commit.developer.id][4] += 1
    return projects_dictionary, developers_dictionary


# For interim report
def day_report(d):
    day_dics = []
    oneday = datetime.timedelta(days=1)
    day = d - oneday
    date_from = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
    date_to = datetime.datetime(d.year, d.month, d.day, 0, 0, 0)
    day_dics = interim_report(date_from, date_to)
    return day_dics[0], day_dics[1], date_from, date_to


# For interim report
def week_report(d):
    week_dics = []
    dayscount = datetime.timedelta(days=d.weekday())
    dayto = d - dayscount
    days = datetime.timedelta(days=7)
    dayfrom = dayto - days
    date_from = datetime.datetime(dayfrom.year,
                                  dayfrom.month, dayfrom.day, 0, 0, 0)
    date_to = datetime.datetime(dayto.year,
                                dayto.month, dayto.day, 0, 0, 0)
    week_dics = interim_report(date_from, date_to)
    return week_dics[0], week_dics[1], date_from, date_to


# For interim report
def month_report(d):
    month_dics = []
    dayscount = datetime.timedelta(days=d.day)
    oneday = datetime.timedelta(days=1)
    dayfrom = d - dayscount
    dayto = dayfrom + oneday
    date_from = datetime.datetime(dayfrom.year, dayfrom.month, 1, 0, 0, 0)
    date_to = datetime.datetime(dayto.year,
                                dayto.month, 1, 0, 0, 0)
    month_dics = interim_report(date_from, date_to)
    return month_dics[0], month_dics[1], date_from, date_to


#  For team report
def team_report_data(projects, developers, date_from, date_to):
    projects_data = {}
    branches_data = {}
    developers_data = {}
    developers_branch_data = {}
    developers_project_data = {}
    try:
        [developers_branch_data, developers_project_data] =\
            report_developers_commits_analyze(projects,
                                              developers,
                                              date_from,
                                              date_to)
        developers_data = report_developers_data(developers_project_data)
        branches_data = report_branches_data(developers_branch_data)
        projects_data = report_projects_data(branches_data)
    except Exception, error:
        print error
    return [projects_data, developers_data, branches_data,
            developers_project_data, developers_branch_data]


# team report to PDF on web
def web_report_to_PDF(projects, developers, date_from, date_to):
    projects_data = {}
    branches_data = {}
    developers_data = {}
    developers_branch_data = {}
    developers_project_data = {}
    headtext = "Red Hat GITVIEW team report"
    timetext =\
        date_from.strftime("%Y.%m.%d") + '_' + date_to.strftime("%Y.%m.%d")
    filename = '_'.join([timetext, 'gitview.pdf'])
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] =\
        'attachment; filename=%s' % filename
    can = Canvas(response)
    can.setFont("Helvetica-Bold", 17.5)
    can.drawString(2.2*inch, 9*inch, "GIT VIEW TEAM DATA REPORT")
    can.setFont("Helvetica", 10.5)
    can.drawString(3.2*inch, 8.5*inch, timetext)
    [projects_data, developers_data, branches_data,
     developers_project_data, developers_branch_data] = \
        team_report_data(projects, developers, date_from, date_to)
    pdf_report(projects_data, developers_data, branches_data,
               developers_project_data, developers_branch_data,
               can, headtext)
    return response


# team report to PDF by using django command
def report_to_PDF(projects, developers, date_from, date_to,
                  filename, timetext, headtext):
    projects_data = {}
    branches_data = {}
    developers_data = {}
    developers_branch_data = {}
    developers_project_data = {}
    can = Canvas(filename)
    can.setFont("Helvetica-Bold", 17.5)
    can.drawString(2.2*inch, 9*inch, "GIT VIEW TEAM DATA REPORT")
    can.setFont("Helvetica", 10.5)
    can.drawString(3.2*inch, 8.5*inch, timetext)
    try:
        [projects_data, developers_data, branches_data,
         developers_project_data, developers_branch_data] =\
            team_report_data(projects, developers, date_from, date_to)
        pdf_report(projects_data, developers_data, branches_data,
                   developers_project_data, developers_branch_data,
                   can, headtext)
    except Exception, error:
        print error


def report_developers_data(developers_project_data):
    developers_data = {}
    for developer in developers_project_data:
        for project in developers_project_data[developer]:
            if developer not in developers_data:
                developers_data[developer] =\
                    developers_project_data[developer][project]
            else:
                developers_data[developer] =\
                    list(map(lambda x: x[0]+x[1],
                         zip(developers_data[developer],
                             developers_project_data[developer][project])))
    return developers_data


def report_projects_data(branches_data):
    projects_data = {}
    for branch in branches_data:
        if branch.project not in projects_data:
            projects_data[branch.project] = branches_data[branch]
        else:
            if projects_data[branch.project] < branches_data[branch]:
                projects_data[branch.project] = branches_data[branch]
    return projects_data


def report_branches_data(developers_branch_data):
    branches_data = {}
    for developer in developers_branch_data:
        for branch in developers_branch_data[developer]:
            if branch not in branches_data:
                branches_data[branch] =\
                    developers_branch_data[developer][branch]
            else:
                branches_data[branch] =\
                    list(map(lambda x: x[0]+x[1],
                         zip(branches_data[branch],
                             developers_branch_data[developer][branch])))
    return branches_data


def report_request_data(request, date_from, date_to):
    projects_developers_selected = []
    developers_selected = []
    report_projects = []
    report_developers = []
    if 'projects' in request.GET and 'developers' in request.GET:
        projects = request.GET.getlist('projects')
        developers = request.GET.getlist('developers')
        if 'all' in projects:
            report_projects += Project.objects.all()
            for project in report_projects:
                projects_developers_selected += project.developers.all()
        else:
            for project_id in projects:
                try:
                    project = Project.objects.get(id=project_id)
                    report_projects.append(project)
                    projects_developers_selected += project.developers.all()
                except ObjectDoesNotExist:
                    pass
        if 'all' in developers:
            developers_selected += Developer.objects.all()
            for developer in developers_selected:
                if developer in projects_developers_selected:
                    report_developers.append(developer)
        else:
            for developer_id in developers:
                try:
                    developer = Developer.objects.get(id=developer_id)
                    if developer in projects_developers_selected:
                        report_developers.append(developer)
                except ObjectDoesNotExist:
                    pass
    return report_projects, report_developers


def report_developers_commits_analyze(projects, developers,
                                      date_from, date_to):
    developers_branch_data = {}
    developers_project_data = {}
    project_developers_list = []
    commits = []
    try:
        for project in projects:
            project_developers_list = project.developers.all()
            for developer in developers:
                if developer in project_developers_list:
                    if developer not in developers_branch_data:
                        developers_branch_data[developer] = {}
                    if developer not in developers_project_data:
                        developers_project_data[developer] = {}
                    commits = Patch.objects.filter(developer=developer,
                                                   project=project,
                                                   submit_date__range=
                                                   (date_from, date_to))
                    for commit in commits:
                        data_list =\
                            [1,
                             commit.total_lines,
                             commit.lines_inserted,
                             commit.lines_deleted]
                        dics = developers_branch_data[developer]
                        br = commit.branch
                        if commit.branch not in dics:
                            developers_branch_data[developer][br] =\
                                data_list
                        else:
                            developers_branch_data[developer][br] =\
                                list(map(lambda x: x[0]+x[1],
                                     zip(developers_branch_data[developer][br],
                                         data_list)))
                else:
                    pass
        for developer in developers:
            for branch in developers_branch_data[developer]:
                if branch.project not in developers_project_data[developer]:
                    developers_project_data[developer][branch.project] =\
                        developers_branch_data[developer][branch]
                else:
                    t_data = developers_project_data[developer][branch.project]
                    tmp_branch = developers_branch_data[developer][branch]
                    if t_data[0] < tmp_branch[0]:
                        developers_project_data[developer][branch.project] =\
                            tmp_branch
    except Exception, error:
        print error
    return developers_branch_data, developers_project_data


def pdf_report(projects_data, developers_data,
               branches_data, developers_project_data,
               developers_branch_data,
               can, headtext):
    y_value = pdf_head(can, headtext)
    y_value = pdf_data_dict(can,
                            "Projects Data",
                            y_value,
                            projects_data)
    y_value = pdf_data_dict(can,
                            "Developers Data",
                            y_value,
                            developers_data)
    y_value = pdf_data_dict_1(can,
                              "Branches Data",
                              y_value,
                              branches_data)
    y_value = pdf_data_dict_2(can,
                              "Developers Data in Projects",
                              y_value,
                              developers_project_data,
                              developers_branch_data)
    can.save()


def pdf_data_dict(canvas, headtext, y_value, data_dict):
    y_value = pdf_check_bottom(canvas, y_value, headtext)
    y_value = pdf_item_head(canvas, y_value, headtext)
    y_value = pdf_check_bottom(canvas, y_value, headtext)
    for item in data_dict:
        y_value -= 0.15
        y_value = pdf_check_bottom(canvas, y_value, headtext)
        canvas.setFont("Helvetica", 9)
        try:
            name_string = item.name
        except:
            name_string = item.kerb_name
        canvas.drawString(1*inch, y_value*inch, name_string)
        x_value = 3.8
        for i in data_dict[item]:
            canvas.drawString(x_value*inch, y_value*inch, str(i))
            x_value += 1
    return y_value - 0.5


def pdf_data_dict_1(canvas, headtext, y_value, data_dict):
    y_value = pdf_check_bottom(canvas, y_value, headtext)
    y_value = pdf_item_head(canvas, y_value, headtext)
    y_value = pdf_check_bottom(canvas, y_value, headtext)
    current_project = ''
    for item in data_dict:
        y_value -= 0.15
        y_value = pdf_check_bottom(canvas, y_value, headtext)
        name_string = item.project.name
        canvas.setFont("Helvetica", 9)
        if name_string != current_project:
            current_project = name_string
            canvas.drawString(1*inch, y_value*inch, name_string)
            y_value -= 0.15
        x_value = 3.7
        for j in data_dict[item]:
            canvas.drawString(1.3*inch, y_value*inch, item.name)
            canvas.drawString(x_value*inch, y_value*inch, str(j))
            x_value += 1
    return y_value - 0.5


def pdf_data_dict_2(canvas, headtext, y_value,
                    developers_project_data,
                    developers_branch_data):
    y_value = pdf_check_bottom(canvas, y_value, headtext)
    y_value = pdf_item_head(canvas, y_value, headtext)
    y_value = pdf_check_bottom(canvas, y_value, headtext)
    for item in developers_project_data:
        y_value = pdf_check_bottom(canvas, y_value, headtext)
        name_string = item.kerb_name
        canvas.setFont("Helvetica", 9)
        if developers_project_data[item]:
            y_value -= 0.15
            canvas.drawString(1*inch, y_value*inch, name_string)
            for project in developers_project_data[item]:
                y_value -= 0.15
                x_value = 3.8
                y_value = pdf_check_bottom(canvas, y_value, headtext)
                canvas.setFont("Helvetica", 9)
                for j in developers_project_data[item][project]:
                    canvas.drawString(1.3*inch, y_value*inch, project.name)
                    canvas.drawString(x_value*inch, y_value*inch, str(j))
                    x_value += 1
                for branch in developers_branch_data[item]:
                    x_value = 3.8
                    if branch.project == project:
                        y_value = pdf_check_bottom(canvas, y_value, headtext)
                        canvas.setFont("Helvetica", 9)
                        y_value -= 0.15
                        for j in developers_branch_data[item][branch]:
                            canvas.drawString(1.5*inch,
                                              y_value*inch,
                                              branch.name)
                            canvas.drawString(x_value*inch,
                                              y_value*inch,
                                              str(j))
                            x_value += 1
            y_value -= 0.1
            canvas.line(1*inch, y_value*inch, 7.5*inch, y_value*inch)
    return y_value - 0.5


# For drwing PDF report
def pdf_head(canvas, headtext):
    canvas.showPage()
    canvas.setFont("Helvetica-Bold", 11.5)
    canvas.drawString(1*inch, 10.5*inch, headtext)
    canvas.rect(1*inch, 10.3*inch, 6.5*inch, 0.12*inch, fill=1)
    return 10


# For drwing PDF report
def pdf_item_head(canvas, y_value, headtext):
    canvas.setFont("Helvetica-Bold", 11.5)
    canvas.drawString(1*inch, y_value*inch, headtext)
    y_value -= 0.1
    canvas.line(1*inch, y_value*inch, 7.5*inch, y_value*inch)
    y_value -= 0.15
    canvas.drawString(1*inch, y_value*inch, "Name")
    canvas.drawString(3.8*inch, y_value*inch, "Commits")
    canvas.drawString(4.8*inch, y_value*inch, "Lines")
    canvas.drawString(5.8*inch, y_value*inch, "Added(+)")
    canvas.drawString(6.8*inch, y_value*inch, "Deleted(-)")
    return y_value - 0.25


# For drwing PDF report
def pdf_check_bottom(canvas, y_value, headtext):
    if y_value <= 1.5:
        canvas.showPage()
        y_value = 11
        y_value = pdf_item_head(canvas, y_value, headtext)
    return y_value


# inbuild tools
def checkout_branch(project_dir, branch):
    try:
        os.chdir(project_dir)
    except Exception, error:
        print error
    cmd = ' '.join(['git checkout', branch])
    try:
        os.system(cmd)
    except Exception, error:
        print error


def total_data(commit_list):
    total_data = [0, 0, 0]
    if not commit_list:
        return commit_list
    else:
        for commit in commit_list:
            total_data[0] += commit.lines_inserted
            total_data[1] += commit.lines_deleted
            total_data[2] += commit.total_lines
        return total_data


def patch_type_data(conf, name):
    classification_list = {'REV': 0, 'SQL': 0, 'FIX': 0, 'DOC': 0, 'OTR': 0}
    if conf == 'pro':
        project = Project.objects.get(name=name)
        if project.id:
            commit_list = Patch.objects.filter(project=project)
        if commit_list:
            for commit in commit_list:
                if commit.classification in classification_list:
                    classification_list[commit.classification] += 1
    elif conf == 'dev':
        developer = Developer.objects.get(kerb_name=name)
        if developer.id:
            commit_list = Patch.objects.filter(developer=developer)
        if commit_list:
            for commit in commit_list:
                if commit.classification in classification_list:
                    classification_list[commit.classification] += 1
    return classification_list


def rewrite_templates(report_dir):
    os.chdir(report_dir)
    files = ['index.html', 'activity.html',
             'authors.html', 'files.html', 'lines.html', 'tags.html']
    for template in files:
        with open(template, "r+") as f:
            d = f.read()
            d.replace('gitstats.css', '/static/gitstats.css')
            f.seek(0)
            f.write(d)


def move_templates(out_dir, to_dir):
    os.chdir(out_dir)
    files = ['index.html', 'activity.html',
             'authors.html', 'files.html', 'lines.html', 'tags.html']
    for template in files:
        cmd = ' '.join(['mv', template, to_dir])
        try:
            os.system(cmd)
        except Exception, error:
            print error


def get_date_range(request):
    if 'year_from' and 'month_from' and 'day_from' and\
            'year_to' and 'month_to' and 'day_to' in request.GET:
        try:
            y = request.GET['year_from']
            m = request.GET['month_from']
            d = request.GET['day_from']
            date_from = datetime.datetime(int(y), int(m), int(d), 0, 0, 0)
            y = request.GET['year_to']
            m = request.GET['month_to']
            d = request.GET['day_to']
            date_to = datetime.datetime(int(y), int(m), int(d), 0, 0, 0)
        except Exception, error:
            print error
    else:
        date_from = datetime.datetime(2005, 1, 1, 0, 0, 0)
        date_to = date_from
    return date_from, date_to
