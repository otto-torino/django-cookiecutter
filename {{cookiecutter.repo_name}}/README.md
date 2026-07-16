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

## Deploy (staging & production)

Both environments run in Docker using the same convention as the other projects
on the self-hosted `zoro` runner. They are structurally identical and differ
only in git branch, published port, and GitHub Environment:

| | Staging | Production |
|---|---|---|
| GitHub Actions workflow | `.github/workflows/deploy_staging.yml` | `.github/workflows/deploy_production.yml` |
| Compose file | `docker-compose.staging.yml` | `docker-compose.production.yml` |
| Deploys on push to | `staging` | `main` |
| Published port (loopback) | `127.0.0.1:{{ cookiecutter.staging_port }}` | `127.0.0.1:{{ cookiecutter.production_port }}` |
| GitHub Environment | `staging` | `production` |

For each environment:

- the app image contains Gunicorn **and** PostgreSQL (single self-contained
  container);
- the stack publishes only its loopback port — no Traefik, no external network;
- the host's Nginx routes the public domain to that loopback port;
- Certbot on the host manages the public TLS certificate;
- `.env.deploy` is generated from the GitHub Environment secrets/variables and
  removed after the job.

### GitHub configuration

Create **two** GitHub Environments — `staging` and `production` — and configure
each one independently (a project has both `staging` and `main` branches, so the
same secret names resolve to different values per Environment):

- **Required Environment Secrets:** `SECRET_KEY`, `DB_NAME`, `DB_USER`,
  `DB_PASSWORD`.
- **Required Environment Variables:** `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
  (e.g. `esempio.com` / `https://esempio.com` — comma-separate multiple values).
- **Optional Environment Secret:** `WEBHOOK_KCHAT` (KChat deploy notifications;
  skipped if empty).

The deploy **will not start** unless every required secret and variable is set
for the target Environment: the workflow aborts with an `::error::` before
building, and the Compose files declare these values as mandatory
(`${VAR:?...}`) so the container also refuses to come up without them. There is
no baked domain fallback.

### Nginx / TLS on the server

Configure an Nginx virtual host that proxies the public domain to the published
port of the target environment (replace `example.com` with the real domain, and
use `{{ cookiecutter.production_port }}` for production, `{{ cookiecutter.staging_port }}`
for staging):

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:{{ cookiecutter.production_port }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the virtual host and validate Nginx:

```bash
ln -s /etc/nginx/sites-available/example.com \
  /etc/nginx/sites-enabled/example.com
nginx -t && systemctl reload nginx
```

After the public DNS points to the server, configure TLS:

```bash
certbot --nginx -d example.com
```

### Manual deploy / logs

To deploy/restart manually from the host (swap `production` for `staging` as
needed):

```bash
docker compose --env-file .env.deploy -f docker-compose.production.yml up -d --build
```

View logs with:

```bash
docker compose -f docker-compose.production.yml logs -f app
```
