#!/usr/bin/env python
# coding=utf-8
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from viewapp import views
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', views.index),
                       url(r'^index$', views.index),
                       url(r'^search$', views.branch_search_show),
                       url(r'^search_report$', views.branch_search_report),
                       url(r'^interim_report$', views.interim_report_toweb),
                       url(r'^team_report$', views.team_report),
                       url(r'^project/\d+$', views.project_report),
                       url(r'^author/\d+$', views.author_search),
                       url(r'^author/search_show$', views.author_search_show),)
