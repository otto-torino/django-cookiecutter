# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Getting Started

- Clone the repository

    ```
    git clone https://github.com/{{ cookiecutter.author }}/{{ cookiecutter.repo_name }}.git
    ```

- Change directory

    ```
    cd [repo_name]/[repo_name]
    ```

- Create a `.env` file

    ```
    touch .env
    ```

- Config the environment

  ```
  dotenv set DJANGO_SETTINGS_MODULE core.settings.local
  dotenv set SECRET_KEY "***"
  dotenv set DB_NAME db{{ cookiecutter.repo_name }}
  dotenv set DB_HOST db
  dotenv set DB_PORT 5432
  dotenv set DB_USER {{ cookiecutter.db_user }}
  dotenv set DB_PASSWORD ***
  dotenv set PYTHONUNBUFFERED true
  dotenv set LC_ALL en_US.UTF-8
  ```

- Create some dirs

    ```
    cd ..
    mkdir .virtualenv
    mkdir logs
    ```

- Start the project

    ```
    make start
    ```

- Enjoy

    ```
    google-chrome http://localhost:8000
    ```

## Makefile (development)

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

## Production / Deploy

Production runs entirely in Docker (app, Postgres, and it's fronted by Traefik as a reverse proxy) and is
deployed by the GitHub Actions workflow at `.github/workflows/deploy.yml`, which triggers on every push to
`main` and runs on a **self-hosted runner with direct access to the target host** (Docker/Docker Compose are
assumed to already be installed there).

Before the first deploy, on the target host:

- Create `{{ cookiecutter.repo_name }}/.env` manually (never committed) with production values for
  `SECRET_KEY`, `DB_NAME`/`DB_USER`/`DB_PASSWORD`, and
  `DJANGO_SETTINGS_MODULE={{ cookiecutter.core_name }}.settings.production`.
- Make sure a shared Traefik instance is already running on the host, attached to an external Docker network
  named `traefik-public` (see the `networks:` section of `docker-compose.production.yml`) with a
  `letsencrypt` cert resolver configured — adjust the labels in that file if your Traefik setup uses
  different names.

After that, deploy is just `git push` to `main`. To deploy/restart manually from the host:

```bash
docker compose -f docker-compose.production.yml up -d --build
```

View production logs with:

```bash
docker compose -f docker-compose.production.yml logs -f app
```
