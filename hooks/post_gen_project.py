#!/usr/bin/env python3

import os
import secrets
import shutil
import subprocess
from collections import OrderedDict
from pathlib import Path

# --- Definitions ---
THEME_APP_NAME = "theme"
context = {{cookiecutter}}
repo_name = context["repo_name"]
core_name = "core"
# The theme app is created by `manage.py tailwind init`, which runs inside the
# inner Django project dir, so on the host it lands at repo_name/theme.
theme_path_on_host = os.path.join(repo_name, THEME_APP_NAME)


def dotenv_value(value):
    """Quote a value for Docker Compose and python-dotenv env files."""
    value = str(value)
    if "\n" in value or "\r" in value:
        raise ValueError("Environment values must not contain newlines.")
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def create_local_env():
    """Create the ignored local environment file required by Compose."""
    env_path = Path(repo_name) / ".env"
    db_password = secrets.token_urlsafe(32)

    values = {
        "DJANGO_SETTINGS_MODULE": "core.settings.local",
        "SECRET_KEY": secrets.token_urlsafe(50),
        "DB_NAME": f"db{repo_name}",
        "DB_HOST": "db",
        "DB_PORT": "5432",
        "DB_USER": context["db_user"],
        "DB_PASSWORD": db_password,
        "POSTGRES_DB": f"db{repo_name}",
        "POSTGRES_USER": context["db_user"],
        "POSTGRES_PASSWORD": db_password,
        "PYTHONUNBUFFERED": "true",
        "LC_ALL": "en_US.UTF-8",
    }
    content = "".join(
        f"{name}={dotenv_value(value)}\n" for name, value in values.items()
    )
    env_path.write_text(content, encoding="utf-8")
    env_path.chmod(0o600)


create_local_env()

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
subprocess.run(
    ["docker", "compose", "-f", "docker-compose.yml", "build", "app"],
    check=True,
)

# 4. Create initial migrations
print("Applying initial migrations...")
migrate_apps = "core tagall pages"
if context["use_cabinet"] == "y":
    migrate_apps += " cabinet"
docker_run(f"cd /home/app/{{cookiecutter.repo_name}}/{{cookiecutter.repo_name}} && python manage.py makemigrations {migrate_apps}")

# 5. Initialize Tailwind CSS and daisyUI
if not os.path.exists(theme_path_on_host):
    print(f"🎨 Initializing Tailwind app ('{THEME_APP_NAME}')...")
    # Name the theme app
    docker_run(
        "cd /home/app/{{cookiecutter.repo_name}}/{{cookiecutter.repo_name}} && "
        f"python manage.py tailwind init --no-input --tailwind-version 4 --app-name {THEME_APP_NAME} --include-daisy-ui"
    )
    
    # Uncomment 'theme' in settings. This runs on the host system.
    os.system(
        f"sed -i \"s/^\\(\\s*\\)#'{THEME_APP_NAME}',/\\1'{THEME_APP_NAME}',/\" {repo_name}/{core_name}/settings/common.py"
    )
    
    # Install npm dependencies (including daisyUI)
    print("🌀 Installing npm dependencies (tailwindcss & daisyui)...")
    docker_run("cd /home/app/{{cookiecutter.repo_name}}/{{cookiecutter.repo_name}} && python manage.py tailwind install")

else:
    print(f"🎨 Tailwind app '{THEME_APP_NAME}' already present, skipping creation.")


# 6. Start services
print("\n🚀 Starting Docker services...")
# Use -d to run in detached mode and not block the terminal
subprocess.run(["docker", "compose", "-f", "docker-compose.yml", "up", "-d"], check=True) 

# 7. Final instructions
print("\n✅ Done! The project is running in the background.")
