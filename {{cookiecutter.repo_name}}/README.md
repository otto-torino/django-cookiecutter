# {{ cookiecutter.project_name }}

![Django 6](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

{{ cookiecutter.project_description }}

## Requirements

- [Git](https://git-scm.com/)
- [Docker Engine](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/install/) (the `docker compose` plugin)

## Local development

When this project is created directly with Cookiecutter, the generation hook
builds the images, initializes the Python virtual environment and Tailwind app,
creates the initial migrations and starts the services automatically.

To set up an existing clone instead:

1. Clone the repository and enter its root directory:

   ```bash
   git clone https://github.com/{{ cookiecutter.author }}/{{ cookiecutter.repo_name }}.git
   cd {{ cookiecutter.repo_name }}
   ```

2. Create the directories used by the bind-mounted virtual environment and
   application logs:

   ```bash
   mkdir -p .virtualenv logs
   ```

3. Create `{{ cookiecutter.repo_name }}/.env` with the local settings:

   ```dotenv
   DJANGO_SETTINGS_MODULE=core.settings.local
   SECRET_KEY=replace-with-a-local-secret-key
   DB_NAME=db{{ cookiecutter.repo_name }}
   DB_HOST=db
   DB_PORT=5432
   DB_USER={{ cookiecutter.db_user }}
   DB_PASSWORD={{ cookiecutter.db_user_pwd }}
   PYTHONUNBUFFERED=true
   LC_ALL=en_US.UTF-8
   ```

4. Build and start the development environment:

   ```bash
   make start
   ```

The first start installs the Python and Tailwind dependencies and applies the
database migrations. The local services are:

| Service | Address | Description |
|---|---|---|
| Django | <http://localhost:8000> | Development server |
| MailHog | <http://localhost:8025> | Email web interface |
| PostgreSQL | `localhost:5434` | Database access from the host |
| debugpy | `localhost:5678` | Python debugger |

## Development commands

Run these commands from the repository root:

| Command | Description |
|---|---|
| `make start` | Start the development environment |
| `make stop` | Stop the development environment |
| `make clean` | Remove containers and volumes |
| `make shell` | Open a shell in the app container |
| `make createsuperuser` | Create a Django superuser |
| `make manage cmd="..."` | Run a Django management command |
| `make reset-db` | Drop and recreate all tables in the local database |

For example:

```bash
make manage cmd="migrate"
```

## Deployments

Staging and production use the same Docker architecture on the
self-hosted `zoro` runner. They differ by branch, published loopback port and
GitHub Environment:

| | Staging | Production |
|---|---|---|
| Workflow | `.github/workflows/deploy_staging.yml` | `.github/workflows/deploy_production.yml` |
| Compose file | `docker-compose.staging.yml` | `docker-compose.production.yml` |
| Deploys on push to | `staging` | `main` |
| Published address | `127.0.0.1:{{ cookiecutter.staging_port }}` | `127.0.0.1:{{ cookiecutter.production_port }}` |
| GitHub Environment | `staging` | `production` |

In both environments:

- the application image contains Gunicorn and PostgreSQL in one container;
- an internal Nginx container serves static files and uploaded media, then
  proxies dynamic requests to Gunicorn;
- database, static files and uploaded media use environment-specific named
  Docker volumes shared with Nginx where needed;
- only internal Nginx is exposed on the environment's `127.0.0.1` port;
- the host's Nginx instance proxies the public domain to that loopback port;
- Certbot on the host manages TLS;
- the workflow creates `.env.deploy` from GitHub configuration and removes it
  after the deployment.

### GitHub configuration

Create the `staging` and `production` GitHub Environments and configure each one
independently.

Required Environment secrets:

- `SECRET_KEY`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

Required Environment variables:

- `ALLOWED_HOSTS`, for example `example.com,www.example.com`
- `CSRF_TRUSTED_ORIGINS`, for example
  `https://example.com,https://www.example.com`

`WEBHOOK_KCHAT` is an optional Environment secret used for deployment
notifications. The workflow skips the notification when it is empty.

The workflow validates every required value before building. The Compose files
also declare those values as mandatory, so a deployment cannot silently start
with fallback credentials or domains.

### Nginx and TLS

Create one Nginx virtual host for each environment. Replace `example.com` and
the port below with the target environment's domain and port
(`{{ cookiecutter.production_port }}` for production or
`{{ cookiecutter.staging_port }}` for staging):

The host does not need direct access to Docker volumes: the internal Nginx
container mounts static and media volumes read-only and serves them itself.
Do not add `/static/` or `/media/` aliases to the host configuration: the
catch-all proxy below forwards those requests to internal Nginx, which handles
them before proxying dynamic requests to Gunicorn.

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com;
    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:{{ cookiecutter.production_port }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

Enable and validate the virtual host:

```bash
ln -s /etc/nginx/sites-available/example.com \
  /etc/nginx/sites-enabled/example.com
nginx -t && systemctl reload nginx
```

After the public DNS points to the server, enable TLS:

```bash
certbot --nginx -d example.com
```

### Manual deployment

For a manual deployment, create `.env.deploy` in the repository root. The file
is ignored by Git and must be protected as a secret:

```dotenv
SECRET_KEY=replace-with-a-production-secret-key
ALLOWED_HOSTS=example.com
CSRF_TRUSTED_ORIGINS=https://example.com
DB_NAME={{ cookiecutter.repo_name | replace('-', '_') }}
DB_USER={{ cookiecutter.db_user }}
DB_PASSWORD=replace-with-a-database-password
APP_PORT={{ cookiecutter.production_port }}
```

Deploy or restart production with:

```bash
docker compose --env-file .env.deploy -f docker-compose.production.yml \
  up -d --build --force-recreate --remove-orphans
```

For staging, use `docker-compose.staging.yml` and set
`APP_PORT={{ cookiecutter.staging_port }}`.

Follow the container logs without requiring `.env.deploy`:

```bash
docker logs -f {{ cookiecutter.repo_name }}_production
```

Use `{{ cookiecutter.repo_name }}_staging` for staging.

Follow the internal Nginx logs with:

```bash
docker logs -f {{ cookiecutter.repo_name }}_production_nginx
```
