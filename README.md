# Django Cookiecutter

Yet another django cookiecutter template.

> It provides a fully working dev environment in a docker container with volume binding in order to have changes to the codebase immediately be reflected in the container. Ansible commands to setup the remote machine and fabric scripts with many deploy utilities.

## Dependencies

* [cookiecutter](https://github.com/cookiecutter/cookiecutter)
* [docker-compose](https://docs.docker.com/)

## Features

- local environment running inside 2 docker containers, one for the app and one for the database
- development ready django project with all packages installed and database created and ready to go
- set of bin commands to perform common tasks
- set of production bin commands to perform machine setup (ansible) and deploy (fabric)

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

| Question | Type | Default | Description |
|----------|------|---------|-------------|
| Project Name | String | My New Project | The project name, site title |
| Project Description | String | My New Project description | The project description, site meta description |
| Repo Name | String | `{{cookiecutter.project_name\|lower\|replace(' ', '-')}}` | The repository name |
| Core Name | String | core | Name of the main application module |
| Admin | Enum<br>django-baton \| default \| django-suit \| django-grappelli | django-baton | The admin application |
| Use filer | Boolean<br>y/n | n | Whether to install django-filer or not |
| Use disqus | Boolean<br>y/n | n | Whether to install django-disqus or not |
| Language Code | String | en | The language code django setting |
| Timezone | String | Europe/Rome | The timezone django setting |
| Author | String | otto | The application author |
| Email | String | web.sites.logs@gmail.com | The admin e-mail used to send erro e-mails with trace |
| Ubuntu Version | Enum<br>16.04 \| 18.04 \| latest  | 18.04 | The ubuntu version used for the docker container |
| Remote User | String | `{{cookiecutter.repo_name}}` | The remote user used during deploy |
| Remote Password | String | | The remote user password |
| Remote Root MySQL Password | String | | The root password for the remote MySQL installation |
| Domain | String | | The domain of the deployed application |
| Db User | String | `{{cookiecutter.repo_name}}` | Remote database user used by the application |
| Db User Password | String | | Remote database user password |
| Web App Dir | String | `/home/{{ cookiecutter.remote_user }}/www/{{ cookiecutter.repo_name }}` | Deploy path of the application |

## CLI

### Autocompletion

The provided cli supports autocompletion through [argcomplete](https://github.com/kislyuk/argcomplete). You need to install it on your machine and activate it globally.

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

