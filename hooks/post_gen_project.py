#!/usr/bin/env python3

##
# Does the following, all inside a docker container:
#
# 1 - Enables gitignore
# 2 - Installs system required packages
# 3 - Creates a new database
# 4 - Creates a virtualenv
# 5 - Installs app requirements
# 6 - Db initial migration
# 7 - Repository initialization
# 8 - Installs sass gem
# 9 - Activates the created virtualenv
##

import os
import shutil
from collections import OrderedDict

context = {{ cookiecutter }}

if context['admin'] != 'django-baton':
    print('\n')
    print('POST HOOK' + '\n')
    print('removing unused baton and constance admin template' + '\n')
    shutil.rmtree('./{{ cookiecutter.repo_name }}/{{ cookiecutter.core_name }}/templates/admin')

shutil.move('gitignore', '.gitignore')
# os.system('docker-compose -f docker-compose.yml build --no-cache')
os.system('mkdir .virtualenv')
os.system('docker-compose -f docker-compose.yml up')
