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

2. Create the application log directory:

   ```bash
   mkdir -p logs
   ```

3. Create `{{ cookiecutter.repo_name }}/.env` with the local settings:

   ```dotenv
   DJANGO_SETTINGS_MODULE=core.settings.local
   SECRET_KEY=replace-with-a-local-secret-key
   DB_NAME=db{{ cookiecutter.repo_name }}
   DB_HOST=db
   DB_PORT=5432
   DB_USER={{ cookiecutter.db_user }}
   DB_PASSWORD=replace-with-a-local-password
   POSTGRES_DB=db{{ cookiecutter.repo_name }}
   POSTGRES_USER={{ cookiecutter.db_user }}
   POSTGRES_PASSWORD=replace-with-the-same-local-password
   PYTHONUNBUFFERED=true
   LC_ALL=en_US.UTF-8
   ```

   Protect the credentials from other local users:

   ```bash
   chmod 600 {{ cookiecutter.repo_name }}/.env
   ```

4. Build and start the development environment:

   ```bash
   make start
   ```

The first start builds the local image with the Python dependencies, installs
the Tailwind dependencies and applies the database migrations. Subsequent
starts reuse Docker's build cache; changing a requirements file rebuilds the
dependency layer. All published development ports listen only on
`127.0.0.1`; they are not exposed to the local network. The services are:

| Service | Address | Description |
|---|---|---|
| Django | <http://localhost:8000> | Development server |
| MailHog | <http://localhost:8025> | Email web interface |
| PostgreSQL | `127.0.0.1:5434` | Authenticated database access from the host |
| debugpy | `localhost:5678` | Python debugger |

The containers do not mount the host's SSH directory or private keys and run
without additional tracing capabilities. If a project later needs private Git
dependencies, use an explicit SSH agent or BuildKit SSH mount for that install
step instead of mounting `~/.ssh` into a long-running container.

## Development commands

Run these commands from the repository root:

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

## Page access policy

Page visibility is centralized and shared by page views, search, sitemaps and
template tags:

- published pages without access restrictions are public;
- restricted pages without selected users or groups are available to any
  authenticated user;
- when users or groups are selected, access is granted to explicitly selected
  users or members of an allowed group;
- users with the `pages.change_page` permission can preview drafts and
  restricted pages;
- sitemaps contain only public pages for the current site.

Every model inheriting from `Searchable` must explicitly implement
`get_search_queryset(request)` and return only the objects the current request
is allowed to discover. Search fails with `ImproperlyConfigured` when this
policy is omitted, preventing a new searchable model from exposing all its
records by default.

## Remote RSS feeds

RSS blocks fetch only HTTP or HTTPS URLs that resolve exclusively to public IP
addresses. Redirects are validated again, responses have timeout and size
limits, successful downloads are cached, and feed text and links are sanitized
before rendering. RSS previews require a staff account, while public RSS block
endpoints inherit the access policy of their page.

The limits can be customized in Django settings:

| Setting | Default | Description |
|---|---:|---|
| `RSS_FEED_TIMEOUT` | `5` | Network timeout in seconds |
| `RSS_FEED_MAX_BYTES` | `2097152` | Maximum response size |
| `RSS_FEED_CACHE_TIMEOUT` | `300` | Successful response cache duration in seconds |
| `RSS_FEED_MAX_REDIRECTS` | `3` | Maximum number of redirects |

## Map content safety

Map coordinates are stored as structured JSON and validated according to their
shape, including geographic ranges and circle radius. Map data is transferred
to JavaScript through Django's `json_script`; popup names and captions are
assigned with `textContent`, and links accept only relative, HTTP or HTTPS URLs.
Invalid legacy values are omitted from rendering instead of being interpreted
as code.

## Deployments

Staging and production use the same Docker architecture on the
self-hosted `zoro` runner. They differ by branch, published loopback port and
GitHub Environment:

| | Staging | Production |
|---|---|---|
| Workflow | `.github/workflows/deploy_staging.yml` | `.github/workflows/deploy_production.yml` |
| Compose file | `docker-compose.staging.yml` | `docker-compose.production.yml` |
| Deploys on push to | `staging` | `main` |
| Global GitHub port variable | `{{ cookiecutter.repo_name | upper | replace('-', '_') }}_STAGING_PORT` | `{{ cookiecutter.repo_name | upper | replace('-', '_') }}_PRODUCTION_PORT` |
| GitHub Environment | `staging` | `production` |

In both environments:

- the application image contains Gunicorn and PostgreSQL in one container;
- `tini` forwards container signals to an entrypoint that stops Gunicorn and
  PostgreSQL cleanly, with a 60-second shutdown grace period;
- an internal Nginx container serves static files and uploaded media, then
  proxies dynamic requests to Gunicorn;
- database, static files and uploaded media use environment-specific named
  Docker volumes shared with Nginx where needed;
- only internal Nginx is exposed on the environment's `127.0.0.1` port;
- Nginx starts only after the combined PostgreSQL/Gunicorn healthcheck passes;
- the host's Nginx instance proxies the public domain to that loopback port;
- Certbot on the host manages TLS;
- workflows keep 30-day PostgreSQL backups under
  `~/backups/{{ cookiecutter.repo_name }}/<environment>/` on the runner;
- deployments wait for container health, run an HTTP smoke test and restore the
  previous application image on failure;
- the workflow creates `.env.deploy` from GitHub configuration and removes it
  after the deployment.

Docker excludes `.env*`, private keys, local databases and backup dumps from
every build context. In particular, the transient `.env.deploy` is never sent
to the Docker daemon or included in an image layer.

Image rollback does not automatically restore PostgreSQL: migrations should be
backward-compatible. Use the timestamped backup for a deliberate database
restore when a migration itself must be reverted.

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

Required global GitHub Actions variables:

- `{{ cookiecutter.repo_name | upper | replace('-', '_') }}_STAGING_PORT`
- `{{ cookiecutter.repo_name | upper | replace('-', '_') }}_PRODUCTION_PORT`

These variables contain the host loopback ports and must be made available to
this repository.

`WEBHOOK_KCHAT` is an optional Environment secret used for deployment
notifications. The workflow skips the notification when it is empty.

The workflow validates every required value before building. The Compose files
also declare those values as mandatory, so a deployment cannot silently start
with fallback credentials or domains.

Production settings force HTTPS, mark session and CSRF cookies as secure, and
send HSTS with an initial lifetime of one hour. Once HTTPS has operated
reliably, set the optional Environment variable `SECURE_HSTS_SECONDS` to a
longer value such as `31536000`. Keep it at `3600` during initial rollout;
setting it to `0` disables HSTS. Subdomains and browser preload are deliberately
not enabled by default.

### Nginx and TLS

Create one Nginx virtual host for each environment. Replace `example.com` and
the port below with the target environment's domain and the value of its global
GitHub port variable:

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
        proxy_pass http://127.0.0.1:PRODUCTION_PORT;
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

### Database backups and restore

Before every update of an existing environment, its workflow stores a
custom-format PostgreSQL dump on the self-hosted runner:

```text
~/backups/{{ cookiecutter.repo_name }}/staging/database_YYYYMMDDTHHMMSSZ.dump
~/backups/{{ cookiecutter.repo_name }}/production/database_YYYYMMDDTHHMMSSZ.dump
```

The directory uses the repository slug (`repo_name`), not the human-readable
project name. Dumps older than 30 days are removed after a successful new
backup. List the available production backups with:

```bash
ls -lh ~/backups/{{ cookiecutter.repo_name }}/production/
```

Application rollback does not restore the database automatically. Restore a
dump only after confirming that application and migration versions require it:
the operation below replaces the current database contents.

Select the environment and backup, validate the dump, and create an additional
pre-restore snapshot:

```bash
ENVIRONMENT=production
APP_CONTAINER="{{ cookiecutter.repo_name }}_${ENVIRONMENT}"
NGINX_CONTAINER="{{ cookiecutter.repo_name }}_${ENVIRONMENT}_nginx"
BACKUP="$HOME/backups/{{ cookiecutter.repo_name }}/${ENVIRONMENT}/database_TIMESTAMP.dump"
BACKUP_DIR="$HOME/backups/{{ cookiecutter.repo_name }}/${ENVIRONMENT}"

docker exec -i "$APP_CONTAINER" pg_restore --list < "$BACKUP" >/dev/null

PRE_RESTORE="$BACKUP_DIR/pre_restore_$(date -u +%Y%m%dT%H%M%SZ).dump"
docker exec "$APP_CONTAINER" sh -c \
  'PGPASSWORD="$DB_PASSWORD" pg_dump --host 127.0.0.1 --username "$DB_USER" --dbname "$DB_NAME" --format custom' \
  > "$PRE_RESTORE"
chmod 600 "$PRE_RESTORE"
```

Stop public traffic, restore in a single transaction, verify container health,
then restart Nginx:

```bash
docker stop "$NGINX_CONTAINER"
docker exec -i "$APP_CONTAINER" sh -c \
  'PGPASSWORD="$DB_PASSWORD" pg_restore --host 127.0.0.1 --username "$DB_USER" --dbname "$DB_NAME" --clean --if-exists --no-owner --single-transaction' \
  < "$BACKUP"
docker exec "$APP_CONTAINER" /healthcheck.sh
docker start "$NGINX_CONTAINER"
```

If the restore or healthcheck fails, leave Nginx stopped and investigate before
making the site public again. Use `ENVIRONMENT=staging` for staging.

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
APP_PORT=PRODUCTION_PORT
SECURE_HSTS_SECONDS=3600
```

Deploy or restart production with:

```bash
docker compose --env-file .env.deploy -f docker-compose.production.yml \
  up -d --build --force-recreate --remove-orphans \
  --wait --wait-timeout 180
```

Replace `PRODUCTION_PORT` with the value of
`{{ cookiecutter.repo_name | upper | replace('-', '_') }}_PRODUCTION_PORT`.
For staging, use `docker-compose.staging.yml` and the value of
`{{ cookiecutter.repo_name | upper | replace('-', '_') }}_STAGING_PORT`.

Follow the container logs without requiring `.env.deploy`:

```bash
docker logs -f {{ cookiecutter.repo_name }}_production
```

Use `{{ cookiecutter.repo_name }}_staging` for staging.

Follow the internal Nginx logs with:

```bash
docker logs -f {{ cookiecutter.repo_name }}_production_nginx
```
