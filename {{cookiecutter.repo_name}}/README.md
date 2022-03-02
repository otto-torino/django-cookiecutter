# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Getting Started

- clone the repository    
    ```
    $ git clone https://github.com/{{ cookiecutter.author }}/{{ cookiecutter.repo_name }}.git
    ```
- cd the new project    
    ```
    $ cd [repo_name]/[repo_name]
    ```
- create a `.env` file
    ```
    $ touch .env
    ```
- config the environment    
  ```
  $ dotenv set DJANGO_SETTINGS_MODULE core.settings.local
  $ dotenv set SECRET_KEY "***"
  $ dotenv set DB_NAME db{{ cookiecutter.repo_name }}
  $ dotenv set DB_HOST db
  $ dotenv set DB_PORT 5432
  $ dotenv set DB_USER {{ cookiecutter.db_user }}
  $ dotenv set DB_PASSWORD ***
  $ dotenv set PYTHONUNBUFFERED true
  $ dotenv set LC_ALL en_US.UTF-8
  $ dotenv set REMOTE_USER ***
  $ dotenv set REMOTE_USER_PWD ***
  $ dotenv set REMOTE_DB ***
  $ dotenv set REMOTE_DB_USER ***
  $ dotenv set REMOTE_DB_PASSWORD ***
  ```
- create some dirs
    ```
    $ cd ..
    $ mkdir .virtualenv
    $ mkdir logs
    ```
- start
    ```
    $ ./cli.py --start
    ```
- enjoy    
    ```
    $ google-chrome http://localhost:8000
    ```

## CLI (development, remote setup and deploy)

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
