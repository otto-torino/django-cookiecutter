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

context = {{cookiecutter}}

if context["use_cabinet"] != "y":
    shutil.rmtree("./{{ cookiecutter.repo_name }}/cabinet")

if context["use_translations"] != "y":
    os.remove("./{{ cookiecutter.repo_name }}/pages/translation.py")
    os.remove("./{{ cookiecutter.repo_name }}/cabinet/translation.py")
    os.remove(
        "./{{ cookiecutter.repo_name }}/{{ cookiecutter.core_name }}/translation.py"
    )

shutil.move("gitignore", ".gitignore")

print("📦 Building Docker images...")

subprocess.run(["mkdir", ".virtualenv"], check=True)
subprocess.run(["docker", "compose", "-f", "docker-compose.yml", "build"], check=True)

migrate_apps = "core pages"
if context["use_cabinet"] == "y":
    migrate_apps += " cabinet"
subprocess.run(
    [
        "docker",
        "compose",
        "-f",
        "docker-compose.yml",
        "run",
        "--rm",
        "app",
        "bash",
        "-c",
        "source /home/app/venv/bin/activate && cd /home/app/{{cookiecutter.repo_name}}/{{cookiecutter.repo_name}} && python manage.py makemigrations %s"
        % migrate_apps,
    ],
    check=True,
)

if not os.path.exists(theme_path):
    print("🎨 Initializing Tailwind app (theme)...")
    subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            "docker-compose.yml",
            "run",
            "--rm",
            "app",
            "bash",
            "-c",
            "source /home/app/venv/bin/activate && cd /home/app/{{cookiecutter.repo_name}}/{{cookiecutter.repo_name}} && python manage.py tailwind init",
        ],
        check=True,
    )
    os.system(
        "sed -i \"s/^\\(\\s*\\)#'theme',/\\1'theme',/\" {{ cookiecutter.repo_name }}/{{ cookiecutter.core_name }}/settings/common.py"
    )
else:
    print("🌀 Tailwind app already present, skipping creation.")

subprocess.run(["docker", "compose", "-f", "docker-compose.yml", "up"], check=True)

print("\n✅ Done! You can now start the project!\n")
