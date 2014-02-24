# All operations will happen in the /tmp directory, and code will cloned from
# the remote repository, that is it's promised that make is based on the latest
# code.

PYTHON=/usr/bin/python
RPM_BUILD=/usr/bin/rpmbuild

PROJECT_CODE_NAME=gitview
WORKING_DIR=/tmp/$(PROJECT_CODE_NAME)-making
RPMBUILD_ROOT=$(HOME)/rpmbuild
REPOSITORY=https://github.com/vince67/gitview.git
BUILD_BRANCH=develop

.PHONY: help pydist-package rpm-package pydist-install rpm-install

help:
	@echo "usage: make [commands]"
	@echo
	@echo "Package will be made upon develop branch by default. If you want to build upon"
	@echo "any other branch, give the branch name to BUILD_BRANCH."
	@echo 
	@echo "commands:"
	@echo "    pydist-package: make Python distribution package"
	@echo "    rpm-package:    make RPM package"
	@echo "    pydist-install: install gitview via Python distribution package"
	@echo "    rpm-install:    install gitview via RPM package"
	@echo "    install:        equivlent to rpm-install"
	@echo "    clean:          remove all files generated during packaging and installation"

pydist-package: clean
	@echo "Make Python distribution package"
	mkdir $(WORKING_DIR)
	cd $(WORKING_DIR); git clone -q -b $(BUILD_BRANCH) $(REPOSITORY)
	cd $(WORKING_DIR)/$(PROJECT_CODE_NAME); $(PYTHON) setup.py sdist --format=gztar
	echo "Wrote: `find $(WORKING_DIR)/$(PROJECT_CODE_NAME)/dist/ -type f`"

rpm-package: pydist-package
	@echo "Make rpm package"
	cd $(WORKING_DIR)/$(PROJECT_CODE_NAME); \
		cp dist/*.tar.gz $(RPMBUILD_ROOT)/SOURCES && \
		cp gitview.spec $(RPMBUILD_ROOT)/SPECS 
	cd $(RPMBUILD_ROOT)/SPECS; $(RPM_BUILD) -ba gitview.spec

pydist-install: pydist-package
	@echo "Install via Python distribution"
	cd $(WORKING_DIR)/$(PROJECT_CODE_NAME); $(PYTHON) setup.py install

rpm-install: rpm-package
	@echo "Install via RPM"
	sudo yum install `find $(RPMBUILD_ROOT)/RPMS -type f -name "*$(PROJECT_CODE_NAME)*rpm"`

install: rpm-install

clean:
	rm -rf $(WORKING_DIR)
	# Remove RPM package generated last time
	rm -f `find $(RPMBUILD_ROOT)/SRPMS -type f -name "*$(PROJECT_CODE_NAME)*src.rpm" | xargs`
	rm -f `find $(RPMBUILD_ROOT)/RPMS -type f -name "*$(PROJECT_CODE_NAME)*rpm" | xargs`
