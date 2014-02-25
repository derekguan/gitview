# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


PACKAGE_NAME = 'gitview'
PACKAGE_DESCRIPTION = ''


def read(filename):
    return open(filename, 'r').read()


setup(
    name=PACKAGE_NAME,
    version=read('VERSION.txt'),
    description=PACKAGE_DESCRIPTION,
    long_description=read('README.md'),
    author='Zhilong Yang',
    author_email='nuovince@gmail.com',
    url='https://github.com/vince67/gitview.git',
    license='GPLv3',
    keywords='git statistics',

    install_requires=[
        'reportlab>=2.5',
    ],

    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={'': ['viewapp/migrations/']},
)
