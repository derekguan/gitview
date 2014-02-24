import os

from gitview.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gitview',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Following settings must be changed for server environment

PROJECT_DATA_ROOT = '/usr/share/gitview'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DATA_ROOT, 'templates'),
)

# Path to static files, that should be /usr/share/gitview/media
STATIC_ROOT = os.path.join(PROJECT_DATA_ROOT, 'static')


GITVIEW_DATA_ROOT = '/var/gitview'

# Path to store PDF report files
PDF_REPORTFILES = os.path.join(GITVIEW_DATA_ROOT, 'pdfs')

# Viewapp will clone projects to this path
PROJECT_DIR = os.path.join(GITVIEW_DATA_ROOT, 'projects')
