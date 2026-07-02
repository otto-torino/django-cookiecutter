# Django Cookiecutter

Yet another django cookiecutter template.

> It provides a fully working dev environment in a docker container, a Makefile to perform common tasks, and a fully Dockerized production setup deployed via GitHub Actions.

## Dependencies

* [cookiecutter](https://github.com/cookiecutter/cookiecutter)
* [docker-compose](https://docs.docker.com/)

> Please follow [this article](https://www.jujens.eu/posts/en/2017/Jul/02/docker-userns-remap/) in order to use Linux user namespaces to fix permissions in docker volumes.

## Features

* Local environment running inside 4 docker containers, one for the app, one for the database, one for the mail service and one for tailwind.
* Development ready django project with all packages installed and database created and ready to go.
* Makefile with common dev tasks.
* Fully Dockerized production stack (app + Postgres, fronted by Traefik) deployed via GitHub Actions on a self-hosted runner.

Project details:

* django db settings managed with environment variables
* some must-have (in my opinion) packages installed:
  * [dj-editor-js](https://github.com/otto-torino/django-editor-js)
  * [django-cleanup](https://github.com/un1t/django-cleanup)
  * [django-preferences-utils](https://github.com/otto-torino/django-preferences-utils)
  * [django-user_agents](https://github.com/selwin/django-user_agents)
  * [django-extensions](https://github.com/django-extensions/django-extensions)
  * [django-simple-captcha](https://github.com/mbi/django-simple-captcha)
  * [django-subject-imagefield](https://github.com/otto-torino/django-subject-imagefield)
  * [django-taggit](https://github.com/alex/django-taggit)
  * [sorl-thumbnail](https://github.com/jazzband/sorl-thumbnail)
  * [django-debug-toolbar](https://github.com/django-debug-toolbar/django-debug-toolbar)
  * [django-baton](https://github.com/otto-torino/django-baton)
  * [django-modeltranslation](https://github.com/otto-torino/django-baton) (optional)
  * [django-filer](https://github.com/stefanfoulis/django-filer) (optional)
  * [django-compressor](https://github.com/django-compressor/django-compressor)
  * [django-tailwind](https://github.com/timonweb/django-tailwind)
  * pages with integrated Editor.js

### Frontend

#### Vendor

* tailwind
* air-datepicker
* ramda
* swiper
* tocca

## Getting started

Install cookiecutter

```bash
pip install cookiecutter
```

Install docker-compose, see the [official docs](https://docs.docker.com/compose/install/).

Run the cookiecutter command

```bash
cookiecutter https://github.com/otto-torino/django-cookiecutter
```

Then you should answer some questions:

| Question | Type | Description |
|----------|------|-------------|
| Project Name | String | The project name, site title |
| Project Description | String | The project description, site meta description |
| Repo Name | String | The repository name |
| Core Name | String | Name of the main application module |
| Use filer | Boolean<br>y/n | Whether to install django-filer or not |
| Use cabinet | Boolean<br>y/n | Whether to include custom cabinet app or not |
| Use sorl thumbnail | Boolean<br>y/n | Whether to install sorl-thumbnail or not |
| Use captcha | Boolean<br>y/n | Whether to install django-simple-captcha or not |
| Use Translations        | Boolean<br>y/n | Whether to install django-modeltranslation or not |
| Default language | Enum<br>it \| en | The language code and languages django setting |
| Timezone | String | The timezone django setting |
| Author | String | The application author |
| Email | String | The admin e-mail used to send erro e-mails with trace |
| Ubuntu Version | Enum<br>20.04 \| 22.04 \| latest  | The ubuntu version used for the docker container |
| Domain | String | The domain of the deployed application |
| Db User | String | Database user used by the application (also used by the production Postgres container) |
| Db User Password | String | Database user password |

After that:

Start the project

    make start

Enjoy

## Makefile

Your new cool installation comes with a Makefile you can use to launch commands that will be executed in the docker container.

| Command | Description |
|---------|-------------|
| `make start` | Starts the development environment |
| `make stop` | Stops the development environment |
| `make clean` | Removes containers and volumes |
| `make shell` | Opens a shell in the app container |
| `make createsuperuser` | Creates a superuser account |
| `make manage cmd="..."` | Executes `python manage.py [command]` in the app container |
| `make reset-db` | Drops all tables in the local dev database |

> After the first start, uncomment the theme app inside the settings common file.

## Production / Deploy

Production runs entirely in Docker (app + Postgres containers, fronted by a shared Traefik reverse proxy
already running on the host) and deploys via the `.github/workflows/deploy.yml` GitHub Actions workflow,
triggered on every push to `main` and running on a self-hosted runner with direct access to the target host.
See the generated project's own README for the exact one-time host setup (a manually created `.env` and a
pre-existing `traefik-public` Docker network) and manual deploy/log commands.

## Starting from cloned project

* Create the `.virtualenv` directory into the root directory
* Create the `logs` directory into the root directory
* Create a `.env` file in the `root/project-name/project-name` directory with the following content:

  ```
    DJANGO_SETTINGS_MODULE=core.settings.local
    DB_NAME=...
    DB_HOST=db
    DB_PORT=5432
    DB_USER=...
    DB_PASSWORD=...
    PYTHONUNBUFFERED=true
    LC_ALL=en_US.UTF-8
    SECRET_KEY=...
  ```

* Launch `make start`
