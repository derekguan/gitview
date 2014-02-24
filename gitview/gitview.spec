%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%global pkg_name gitview

Name: python-%{pkg_name}
Version: 0.1.0
Release: 1%{?dist}
Summary: A Web project gathering git data from projects repositories

Group: Development/Languages
License: GPLv3
URL: https://github.com/vince67/gitview.git;a=summary
Source0: %{pkg_name}-%{version}.tar.gz
BuildArch: noarch

BuildRequires:	python-setuptools

Requires:	Django >= 1.5
Requires:	git
Requires:	httpd
Requires:	mod_auth_kerb
Requires:	mod_wsgi
Requires:	MySQL-python
Requires:	crontabs
Requires:	python-reportlab >= 2.5


%description
A Web project gathering git data from projects repositories.


%prep
%setup -q -n %{pkg_name}-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

# Apache conf
install -m 0644 -D -p conf/gitview.conf ${RPM_BUILD_ROOT}%{_sysconfdir}/httpd/conf.d/%{pkg_name}.conf

# Make all necessary directories, including
# 1. project data directory holding all necessary files for gitview running
# 2. runtime data directory holding all data generated during the runtime. For
#    example, the cloned projects, logs produced from gitview features and the
#    scheduled cron job, etc.
# 3. configuration directory holding necessary configuraiton files, including
#    cron job control file for now.

# Project data directory, /usr/share/gitview
# These are necessary for project to run normally.
# Different from that directory that holds data generated during runtime
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/%{pkg_name}

# Project runtime data directories, root is /var/gitview
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/%{pkg_name}
mkdir ${RPM_BUILD_ROOT}%{_localstatedir}/%{pkg_name}/projects
mkdir ${RPM_BUILD_ROOT}%{_localstatedir}/%{pkg_name}/reports
mkdir ${RPM_BUILD_ROOT}%{_localstatedir}/%{pkg_name}/pdfs

# Directory holding cron job logs
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/log/%{pkg_name}

# Configuration directories
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/%{pkg_name}

### End of making directories ###

# Template files locates /usr/share/gitview/templates
cp -r gitview/templates ${RPM_BUILD_ROOT}%{_datadir}/%{pkg_name}/

# static files locates /usr/share/gitview/static
project_lib=${RPM_BUILD_ROOT}%{python_sitelib}/%{pkg_name}
product_module=${project_lib}/%{pkg_name}/product_settings.py
product_module_bak=${product_module}.bak
static_root=${RPM_BUILD_ROOT}%{_datadir}/%{pkg_name}/static/
# Add all app names whose static files are needed to be collected
# Just enter what you write in settings.py
apps_static_collected_from=""

# Make a backup of the product DJANGO_SETTINGS_MODULE, then restore it when
# everything is done well.
cp $product_module $product_module_bak

echo "STATIC_ROOT = '${static_root}'" >> ${product_module}

# Construct and overwrite INSTALLED_APPS to collect static files from all
# necessary apps.
apps_list="'django.contrib.admin', 'django.contrib.staticfiles'"
for app in ${apps_static_collected_from}
do
    apps_list="${apps_list},'${app}',"
done
echo "INSTALLED_APPS = ( ${apps_list} )" >> ${product_module}

# Overwrite database configuration to avoid communicating with real database,
# since collecting static does not need any database operations.
echo "DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'" >> ${product_module}
echo "DATABASES['default']['NAME'] = ':memory:'" >> ${product_module}

django_admin_bins="/usr/bin/django-admin /usr/bin/django-admin.py"
ct_pythonpath=`dirname ${project_lib}`/%{pkg_name}
ct_settings=%{pkg_name}.product_settings
for cmd in ${django_admin_bins}
do
    if [ -e "$cmd" ]
    then
        ${cmd} collectstatic \
            --pythonpath=${ct_pythonpath} \
            --settings=${ct_settings} \
            --noinput
        static_collected=1
        break
    fi
done
if [ ! -v static_collected ]
then
    echo "Cannot find either django-admin or django-admin.py"
    exit 1
fi
mv ${product_module_bak} ${product_module}

%post
# Configure cronjob to generate report regularly
GITVIEW_MANAGE=%{python_sitelib}/%{pkg_name}/manage.py
GITVIEW_SETTINGS_MODULE=gitview.product_settings
GITVIEW_CRON_LOG_FILE=%{_localstatedir}/log/%{pkg_name}/projects_refresh_cron.log
GITVIEW_CRON_CONTROL_FILE=%{_sysconfdir}/%{pkg_name}/refresh_projects.cron
GITVIEW_CRON_JOB="0 6,12,18 * * 1-5 python ${GITVIEW_MANAGE} viewapp_refresh --settings=${GITVIEW_SETTINGS_MODULE} --all >> ${GITVIEW_CRON_LOG_FILE} 2>&1"
# Write the cronjob control file
echo "$GITVIEW_CRON_JOB" > ${GITVIEW_CRON_CONTROL_FILE}
# First, the cron job created previously should be removed.
crontab -u apache -r
crontab -u apache ${GITVIEW_CRON_CONTROL_FILE}

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc MANIFEST.in README.md VERSION.txt
%{python_sitelib}/%{pkg_name}/
%{python_sitelib}/%{pkg_name}-%{version}-py*.egg-info/
%{_datadir}/%{pkg_name}/
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{pkg_name}.conf
%{_sysconfdir}/%{pkg_name}

%defattr(-,apache,apache,-)
%{_localstatedir}/%{pkg_name}
%{_localstatedir}/log/%{pkg_name}


%changelog
* Mon Jan 27 2014 Chenxiong Qi <cqi@redhat.com> - 0.1.0-1
- Bump to version 0.1.0

* Thu Jan 23 2014 Chenxiong Qi <cqi@redhat.com> - 0.0.1-2
- Build RPM package, ready for deployment

* Mon Dec 16 2013 Chenxiong Qi <cqi@redhat.com> - 0.0.1-1
- Initial RPM package build
