#!/usr/bin/env python3

import secrets
import shutil
from collections import OrderedDict  # noqa: F401 - used by rendered context repr
from pathlib import Path

context = {{cookiecutter}}
repo_name = context["repo_name"]
core_name = "core"


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

# Optional module cleanup
if context["use_cabinet"] != "y":
    cabinet_path = Path(repo_name) / "cabinet"
    if cabinet_path.exists():
        shutil.rmtree(cabinet_path)

if context["use_translations"] != "y":
    files_to_remove = [
        Path(repo_name) / "pages" / "translation.py",
        Path(repo_name) / "cabinet" / "translation.py",
        Path(repo_name) / "tagall" / "translation.py",
        Path(repo_name) / core_name / "translation.py",
    ]
    for path in files_to_remove:
        path.unlink(missing_ok=True)

# Cookiecutter cannot render a file named .gitignore directly.
shutil.move("gitignore", ".gitignore")

print("\n✅ Project generated without building images or starting services.")
print("Run `make bootstrap` from the project root when you are ready to set it up.")
