# Django Cookiecutter

Yet another django cookiecutter template.

> It provides a fully working dev environment in a docker container, a convenient cli with autocompletion to perform common tasks, an ansible command to set up the remote machine and fabric scripts with many deploy utilities.

## Dependencies

* [cookiecutter](https://github.com/cookiecutter/cookiecutter)
* [docker-compose](https://docs.docker.com/)

> Please follow [this article](https://www.jujens.eu/posts/en/2017/Jul/02/docker-userns-remap/) in order to use Linux user namespaces to fix permissions in docker volumes.

## Features

- Local environment running inside 2 docker containers, one for the app and one for the database.
- Development ready django project with all packages installed and database created and ready to go.
- Set of bin commands to perform common tasks.
- Set of production bin commands to perform machine setup (ansible) and deploy (fabric).

Project details:

- django db settings managed with environment variables
- some must-have (in my opinion) packages installed:
    - [django-pipeline](https://github.com/cyberdelia/django-pipeline)
    - [django-ckeditor](https://github.com/django-ckeditor/django-ckeditor)
    - [django-cleanup](https://github.com/un1t/django-cleanup)
    - [django-constance](https://github.com/jazzband/django-constance)
    - [django-user_agents](https://github.com/selwin/django-user_agents)
    - [django-extensions](https://github.com/django-extensions/django-extensions)
    - [django-simple-captcha](https://github.com/mbi/django-simple-captcha)
    - [django-subject-imagefield](https://github.com/otto-torino/django-subject-imagefield)
    - [django-taggit](https://github.com/alex/django-taggit)
    - [easy-thumbnails](https://github.com/SmileyChris/easy-thumbnails)
    - [sorl-thumbnail](https://github.com/jazzband/sorl-thumbnail)
    - [django-debug-toolbar](https://github.com/django-debug-toolbar/django-debug-toolbar)
    - [django-baton](https://github.com/otto-torino/django-baton) (optional)
    - [django-suit](http://djangosuit.com/) (optional)
    - [django-grappelli](https://github.com/sehmaschine/django-grappelli) (optional)
    - [django-filer](https://github.com/stefanfoulis/django-filer) (optional)
    - [django-disqus](https://github.com/arthurk/django-disqus) (optional)
    - pages with integrated ckeditor

### Frontend

#### Vendor

- jQuery
- moment.js
- Semantic UI
- FontAwesome
- air-datepicker
- Swiper
- Tocca

## Getting started

Install cookiecutter

```bash
$ pip install cookiecutter
```

Install docker-compose, see the [official docs](https://docs.docker.com/compose/install/).

Run the cookiecutter command

```bash
$ cookiecutter https://github.com/otto-torino/django-cookiecutter
```

Then you should answer some questions:

| Question | Type | Description |
|----------|------|-------------|
| Project Name | String | The project name, site title |
| Project Description | String | The project description, site meta description |
| Repo Name | String | The repository name |
| Core Name | String | Name of the main application module |
| Admin | Enum<br>django-baton \| default \| django-suit \| django-grappelli | The admin application |
| Use filer | Boolean<br>y/n | Whether to install django-filer or not |
| Use disqus | Boolean<br>y/n | Whether to install django-disqus or not |
| Use subject imagefield | Boolean<br>y/n | Whether to install django-subject-imagefield or not |
| Use sorl thumbnail | Boolean<br>y/n | Whether to install sorl-thumbnail or not |
| Use captcha | Boolean<br>y/n | Whether to install django-simple-captcha or not |
| Language Code | String | The language code django setting |
| Timezone | String | The timezone django setting |
| Author | String | The application author |
| Email | String | The admin e-mail used to send erro e-mails with trace |
| Ubuntu Version | Enum<br>16.04 \| 18.04 \| latest  | The ubuntu version used for the docker container |
| Remote User | String | The remote user used during deploy |
| Remote Password | String | The remote user password |
| Domain | String | The domain of the deployed application |
| Db User | String | Remote database user used by the application |
| Db User Password | String | Remote database user password |
| Web App Dir | String | Deploy path of the application |

## CLI

Your new cool installation comes with a command line interface you can use to launch commands that will be executed in the docker container.

| Command | Description |
|---------|-------------|
| `--help` | Prints the help summary |
| `--start` | Starts the development environment |
| `--clean` | Removes containers and volumes |
| `--shell` | Opens a shell in the app container |
| `--createsuperuser` | Creates a superuser account |
| `--manage [command]` | Executes `python manage.py [command]` in the app container |
| `--remote [command]` | Executes a command in the remote production server |

Let's see in the detail the remote commands:

| Remote command | Description |
|----------------|-------------|
| `setup` | Executes the setup of the remote machine (install necessary packages, creates users, folders and db) |
| `createReleaseArchive` | Craetes a release archive in the `releases` folder |
| `deploy` | Performs a deploy in production |
| `rollback` | Rollbacks to the previous release in production |
| `getRemoteRevision` | Returns the current revision deployed in production |
| `dumpDbSnapshot` | Dumps and downloads a production db snapshot |
| `loadDbSnapshot` | Dumps and downloads a production db snapshot and loads it in the local db |
| `loadDb` | Loads the current production db already downloaded in the local db |
| `offline` | Puts the site in maintenance mode |
| `online` | Removes the maintenance mode |
| `reloadServer` | Reloads the web server |
| `restartUwsgi` | Restarts uWSGI service |
| `restart` | Restarts services and reloads the web server |


### Autocompletion

The provided cli supports autocompletion through [argcomplete](https://github.com/kislyuk/argcomplete). If you want to benefit of it (not mandatory), you need to install it on your machine and activate it globally.

#### Ubuntu

```bash
$ pip install argcomplete
$ mkdir ~/.bash_completion.d
$ activate-global-python-argcomplete --dest=~/.bash_completion.d
$ echo ". ~/.bash_completion.d/python-argcomplete" >> ~/.bashrc
```

#### OSX

The problem with OSX is that it comes with a quite old version of bash which does not support all recent source command options.    
Better update it.

```bash
$ brew install bash
$ sudo bash -c 'echo /usr/local/bin/bash >> /etc/shells'
$ chsh -s /usr/local/bin/bash
$ pip install argcomplete
$ activate-global-python-argcomplete
$ echo ". /usr/local/etc/bash_completion.d/python-argcomplete" >> ~/.bashrc
$ echo "[ -r ~/.bashrc ] && source ~/.bashrc" >> ~/.bash_profile
```

## Starting from cloned project

- Create the `.virtualenv` directory into the root directory
- Create the `logs` directory into the root directory
- Create a `.env` file in the `root/project-name/project-name` directory with the following content:
  ```
    DJANGO_SETTINGS_MODULE=core.settings.local
    DB_NAME=...
    DB_HOST=db
    DB_PORT=5432
    DB_USER=...
    DB_PASSWORD=...
    PYTHONUNBUFFERED=true
    LC_ALL=en_US.UTF-8
    REMOTE_USER=...
    REMOTE_USER_PWD=...
    REMOTE_DB=...
    REMOTE_DB_USER=...
    REMOTE_DB_PASSWORD=...
    SECRET_KEY=...
  ```
- Launch `./cli.py --start`

## TODO

- Add bootstrap 5 as cookiecutter option
- Add staging environment
