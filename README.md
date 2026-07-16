# Django Cookiecutter

![Django 6](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Cookiecutter](https://img.shields.io/badge/template-Cookiecutter-D4AA00)

A Cookiecutter template for a Docker-based Django project, with a ready-to-use
local environment and automated staging and production deployments through
GitHub Actions.

## Requirements

- [Cookiecutter](https://cookiecutter.readthedocs.io/)
- [Docker Engine](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/) (the `docker compose` plugin)

On Linux, consider enabling
[Docker user namespace remapping](https://docs.docker.com/engine/security/userns-remap/)
to avoid permission issues with bind-mounted files.

## What is included

The generated project provides:

- Django 6 with PostgreSQL;
- a local Docker Compose stack with the Django app, PostgreSQL, MailHog and a
  Tailwind watcher;
- Tailwind CSS 4 and daisyUI;
- a custom user model, pages, search and an optional file cabinet app;
- Editor.js, django-baton, django-compressor, django-cleanup,
  django-extensions, django-lineup, django-preferences-utils,
  django-subject-imagefield, django-web-components and the bundled `tagall`
  tagging app;
- optional django-modeltranslation and sorl-thumbnail integration;
- a Makefile for common development tasks;
- Docker deployments for staging and production with an internal Nginx serving
  shared static/media volumes, project-specific loopback ports and GitHub
  Actions.

Frontend vendor assets include Air Datepicker, PhotoSwipe, Ramda, Swiper and
Tocca.

## Create a project

Install Cookiecutter:

```bash
python -m pip install cookiecutter
```

Generate the project:

```bash
cookiecutter https://github.com/otto-torino/django-cookiecutter
```

The generator asks for the following values:

| Option | Type | Description |
|---|---|---|
| `project_name` | String | Project name and site title |
| `project_description` | String | Project description and default meta description |
| `repo_name` | String | Repository and Python package directory name |
| `use_cabinet` | `y` / `n` | Include the custom cabinet app |
| `use_sorl_thumbnail` | `y` / `n` | Include sorl-thumbnail |
| `use_translations` | `y` / `n` | Include django-modeltranslation |
| `default_language` | `it` / `en` | Default Django language |
| `timezone` | String | Django and container timezone |
| `author` | String | Repository owner and Django admin name |
| `email` | String | Address that receives Django error emails |
| `db_user` | String | Local PostgreSQL user; also used as the generated default |

After rendering the template, the post-generation hook automatically:

1. creates the ignored local `.env` with a random Django secret and the chosen
   database credentials, using file mode `0600`;
2. removes optional modules that were not selected;
3. builds the local application image with its Python dependencies;
4. creates the initial migrations;
5. initializes the Tailwind app with daisyUI;
6. starts the local stack in the background.

The application is then available at <http://localhost:8000> and the MailHog
interface at <http://localhost:8025>.

> Project generation runs Docker commands and therefore requires a working
> Docker daemon. The generated directory is already initialized for local
> development; use its own README for clone setup and deployment instructions.

## Development commands

Run these commands from the root of the generated project:

| Command | Description |
|---|---|
| `make start` | Build if needed and start the development environment |
| `make build` | Rebuild the local application image |
| `make stop` | Stop the development environment |
| `make clean` | Remove containers and volumes |
| `make shell` | Open a shell in the app container |
| `make createsuperuser` | Create a Django superuser |
| `make manage -- <command> [args]` | Run a Django management command |
| `make reset-db` | Drop and recreate all tables in the local database |

For example:

```bash
make manage -- makemigrations pages
```

## Deployments

The generated project contains separate but equivalent staging and production
deployments:

| | Staging | Production |
|---|---|---|
| Branch | `staging` | `main` |
| Workflow | `deploy_staging.yml` | `deploy_production.yml` |
| Compose file | `docker-compose.staging.yml` | `docker-compose.production.yml` |
| Global GitHub port variable | `<REPO_NAME>_STAGING_PORT` | `<REPO_NAME>_PRODUCTION_PORT` |
| GitHub Environment | `staging` | `production` |

Each deployment runs Django, Gunicorn and PostgreSQL in the application
container. An internal Nginx container serves shared static/media volumes and
proxies dynamic requests to Gunicorn. Only internal Nginx binds to `127.0.0.1`;
the host's Nginx proxies the public domain to that port and Certbot manages TLS.

Before replacing an existing deployment, each workflow creates a PostgreSQL
custom-format dump on the self-hosted runner. Backups are grouped by the
repository slug and environment:

```text
~/backups/<repo_name>/staging/database_YYYYMMDDTHHMMSSZ.dump
~/backups/<repo_name>/production/database_YYYYMMDDTHHMMSSZ.dump
```

Backups are retained for 30 days. Deployments wait for container health and an
HTTP smoke test; on failure the previous application image is restored. The
database is deliberately not restored automatically, avoiding accidental loss
of writes made after the backup. The generated README contains the guarded
manual restore procedure.

Each GitHub Environment must define:

- secrets: `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`;
- variables: `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`;
- optional variable: `SECURE_HSTS_SECONDS` (defaults to `3600`);
- optional secret: `WEBHOOK_KCHAT`, for deploy notifications.

The GitHub organization must also expose the repository-specific Actions
variables `<REPO_NAME>_STAGING_PORT` and `<REPO_NAME>_PRODUCTION_PORT`. The
repository name is uppercased and hyphens are replaced with underscores; for
example, `my-site` uses `MY_SITE_STAGING_PORT` and
`MY_SITE_PRODUCTION_PORT`.

See the generated project's README for Nginx configuration, TLS setup, manual
deploys and log commands.
