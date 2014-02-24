# -*- coding: utf-8 -*-

from django.contrib import admin
from viewapp.models import Developer
from viewapp.models import Project
from viewapp.models import Branch
from viewapp.models import Patch
from viewapp.models import ViewappLog

admin.site.register(Developer)
admin.site.register(Project)
admin.site.register(Branch)
admin.site.register(Patch)
admin.site.register(ViewappLog)
