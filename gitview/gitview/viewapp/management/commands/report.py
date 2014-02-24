# -*- coding: utf-8 -*-

import os
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from optparse import make_option
from django.conf import settings

from django.conf import settings
from viewapp import views
from viewapp.models import Project
from viewapp.models import Developer
from viewapp.models import Patch
from viewapp.models import Branch
from viewapp.models import Project


class Command(BaseCommand):
    "day/week/month report"
    option_list = BaseCommand.option_list + (
        make_option('--day',
                    action='store_true',
                    dest='day',
                    default=False,
                    help="report data of yesterday"),
        make_option('--week',
                    action='store_true',
                    dest='week',
                    default=False,
                    help="report data of last week"),
        make_option('--month',
                    action='store_true',
                    dest='month',
                    default=False,
                    help="report data of last month"),
        make_option('--teamreport',
                    action='store_true',
                    dest='teamreport',
                    default=False,
                    help="report data of team"),
        make_option('--allprojects',
                    action='store_true',
                    dest='allprojects',
                    default=False,
                    help="report data of all projects"),)

    def handle(self, *args, **options):
        d = datetime.datetime.now()
        if options['day']:
            oneday = datetime.timedelta(days=1)
            day = d - oneday
            date_from = datetime.datetime(day.year,
                                          day.month,
                                          day.day,
                                          0, 0, 0)
            date_to = datetime.datetime(d.year, d.month, d.day, 0, 0, 0)
            self.pdf_interim_report(date_from, date_to)
        if options['week']:
            dayscount = datetime.timedelta(days=d.weekday())
            dayto = d - dayscount
            days = datetime.timedelta(days=7)
            dayfrom = dayto - days
            date_from = datetime.datetime(dayfrom.year,
                                          dayfrom.month, dayfrom.day, 0, 0, 0)
            date_to = datetime.datetime(dayto.year,
                                        dayto.month, dayto.day, 0, 0, 0)
            self.pdf_interim_report(date_from, date_to)
        if options['month']:
            dayscount = datetime.timedelta(days=d.day)
            oneday = datetime.timedelta(days=1)
            dayfrom = d - dayscount
            dayto = dayfrom + oneday
            date_from = datetime.datetime(dayfrom.year,
                                          dayfrom.month,
                                          1,
                                          0, 0, 0)
            date_to = datetime.datetime(dayto.year,
                                        dayto.month, 1, 0, 0, 0)
            self.pdf_interim_report(date_from, date_to)
        if options['teamreport']:
            date_from = datetime.datetime(2013, 1, 1, 0, 0, 0)
            date_to = datetime.datetime(2014, 1, 1, 0, 0, 0)
            team_members = ["ctang@redhat.com", "cqi@redhat.com",
                            "dxiao@redhat.com", "fhuang@redhat.com",
                            "hlin@redhat.com", "jianchen@redhat.com",
                            "jianli@redhat.com", "qduanmu@redhat.com",
                            "qwan@redhat.com", "weizhou@redhat.com",
                            "xchu@redhat.com", "xudong@redhat.com",
                            "yuwang@redhat.com", "zheliu@redhat.com",
                            "zyang@redhat.com", "zhouwtlord@gmail.com",
                            "cbtchn@gmail.com", "xychu2008@gmail.com"]
            developers = []
            for email in team_members:
                try:
                    developer = Developer.objects.get(email=email)
                    if developer not in developers:
                        developers.append(developer)
                except ObjectDoesNotExist:
                    pass
            projects = Project.objects.all()
            headtext = "Red Hat HSS team 2013-2014 report"
            timetext = '_'.join([date_from.strftime("%Y.%m.%d"),
                                 date_to.strftime("%Y.%m.%d")])
            filename = '_'.join([timetext, 'teamreport.pdf'])
            filename = os.path.join(settings.PDF_REPORTFILES, filename)
            views.report_to_PDF(projects, developers, date_from, date_to,
                                filename, timetext, headtext)
        if options['allprojects']:
            date_from = datetime.datetime(2013, 1, 1, 0, 0, 0)
            date_to = datetime.datetime(2014, 1, 1, 0, 0, 0)
            developers = Developer.objects.all()
            projects = Project.objects.all()
            headtext = "Red Hat HSS team 2013-2014 report"
            timetext = '_'.join([date_from.strftime("%Y.%m.%d"),
                                 date_to.strftime("%Y.%m.%d")])
            filename = '_'.join([timetext, 'allprojects.pdf'])
            filename = os.path.join(settings.PDF_REPORTFILES, filename)
            views.report_to_PDF(projects, developers, date_from, date_to,
                                filename, timetext, headtext)

    def pdf_interim_report(self, date_from, date_to):
        developers = Developer.objects.all()
        projects = Project.objects.all()
        timetext = '-'.join([date_from.strftime("%Y.%m.%d"),
                             date_to.strftime("%Y.%m.%d")])
        headtext = ' '.join(["Red Hat HSS report", timetext])
        filename = '_'.join([timetext, 'all.pdf'])
        filename = os.path.join(settings.PDF_REPORTFILES, filename)
        views.report_to_PDF(projects, developers, date_from, date_to,
                            filename, timetext, headtext)
