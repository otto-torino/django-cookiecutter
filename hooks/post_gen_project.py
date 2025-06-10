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
import subprocess
import shutil
from collections import OrderedDict


theme_path = os.path.join("theme")

context = {{ cookiecutter }}

if context['admin'] != 'django-baton':
    print('\n')
    print('POST HOOK' + '\n')
    print('removing unused baton admin template' + '\n')
    shutil.rmtree('./{{ cookiecutter.repo_name }}/{{ cookiecutter.core_name }}/templates/admin')

if context['use_cabinet'] != 'y':
    shutil.rmtree('./{{ cookiecutter.repo_name }}/cabinet')

shutil.move('gitignore', '.gitignore')

print("📦 Building Docker images...")
subprocess.run(["docker", "compose", "-f", "docker-compose.yml", "build"], check=True)

if not os.path.exists(theme_path):
    print("🎨 Initializing Tailwind app (theme)...")
    subprocess.run([
        "docker", "compose", "-f", "docker-compose.yml", "run", "--rm", "app",
        "./cli.py", "--manage", "tailwind init" # TODO: DA FIXARE
    ], check=True)
else:
    print("🌀 Tailwind app already present, skipping creation.")

subprocess.run(["docker", "compose", "-f", "docker-compose.yml", "up"], check=True)

print("\n✅ Done! You can now start the project!\n")
