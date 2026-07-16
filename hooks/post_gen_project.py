#!/usr/bin/env python3

import os
import subprocess
import shutil
from collections import OrderedDict

# --- Definitions ---
THEME_APP_NAME = "theme"
theme_path_on_host = os.path.join(THEME_APP_NAME)
context = {{cookiecutter}}
repo_name = context["repo_name"]
core_name = "core"

# --- Helper function for docker commands ---
def docker_run(command, workdir=f"/home/app/{repo_name}"):
    """
    Runs a command inside the 'app' container.
    Defaults the working directory to the project root where manage.py is.
    """
    # The command itself is now prefixed with 'cd' to ensure context
    full_command = f"cd {workdir} && {command}"
    base_cmd = [
        "docker", "compose", "-f", "docker-compose.yml",
        "run", "--rm", "app", "bash", "-c", full_command
    ]
    subprocess.run(base_cmd, check=True)

# 1. Optional module cleanup
if context["use_cabinet"] != "y":
    if os.path.exists(f"./{repo_name}/cabinet"):
        shutil.rmtree(f"./{repo_name}/cabinet")

if context["use_translations"] != "y":
    files_to_remove = [
        f"./{repo_name}/pages/translation.py",
        f"./{repo_name}/cabinet/translation.py",
        f"./{repo_name}/tagall/translation.py",
        f"./{repo_name}/{core_name}/translation.py",
    ]
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)

# 2. Move gitignore
shutil.move("gitignore", ".gitignore")

# 3. Build Docker images
print("📦 Building Docker images...")
subprocess.run(["mkdir", "-p", ".virtualenv"], check=True)
subprocess.run(["docker", "compose", "-f", "docker-compose.yml", "build"], check=True)

# 4. Create virtualenv and install local dependencies
print("Creating virtualenv and installing dependencies...")
docker_run(
    "python3 -m venv /home/app/venv && "
    "source /home/app/venv/bin/activate && "
    f"pip install -r /home/app/{repo_name}/{repo_name}/requirements/local.txt"
)

# 5. Create initial migrations
print("Applying initial migrations...")
migrate_apps = "core tagall pages"
if context["use_cabinet"] == "y":
    migrate_apps += " cabinet"
docker_run(f"source /home/app/venv/bin/activate && cd /home/app/{{cookiecutter.repo_name}}/{{cookiecutter.repo_name}} && python manage.py makemigrations {migrate_apps}")

# 6. Initialize Tailwind CSS and daisyUI
if not os.path.exists(theme_path_on_host):
    print(f"🎨 Initializing Tailwind app ('{THEME_APP_NAME}')...")
    # Name the theme app
    docker_run(
        "source /home/app/venv/bin/activate && "
        "cd /home/app/{{cookiecutter.repo_name}}/{{cookiecutter.repo_name}} && "
        f"python manage.py tailwind init --no-input --tailwind-version 4 --app-name {THEME_APP_NAME} --include-daisy-ui"
    )
    
    # Uncomment 'theme' in settings. This runs on the host system.
    os.system(
        f"sed -i \"s/^\\(\\s*\\)#'{THEME_APP_NAME}',/\\1'{THEME_APP_NAME}',/\" {repo_name}/{core_name}/settings/common.py"
    )
    
    # Install npm dependencies (including daisyUI)
    print("🌀 Installing npm dependencies (tailwindcss & daisyui)...")
    docker_run("source /home/app/venv/bin/activate && cd /home/app/{{cookiecutter.repo_name}}/{{cookiecutter.repo_name}} && python manage.py tailwind install")

else:
    print(f"🎨 Tailwind app '{THEME_APP_NAME}' already present, skipping creation.")


# 7. Start services
print("\n🚀 Starting Docker services...")
# Use -d to run in detached mode and not block the terminal
subprocess.run(["docker", "compose", "-f", "docker-compose.yml", "up", "-d"], check=True) 

# 8. Final instructions
print("\n✅ Done! The project is running in the background.")
