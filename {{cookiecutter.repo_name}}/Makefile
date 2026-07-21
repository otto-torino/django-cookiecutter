.DEFAULT_GOAL := help

.PHONY: help bootstrap start build stop clean shell createsuperuser test manage reset-db

ifeq (manage,$(firstword $(MAKECMDGOALS)))
MANAGE_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
.PHONY: $(MANAGE_ARGS)
$(MANAGE_ARGS):
	@:

else

help:
	@printf '%s\n' \
		'Available commands:' \
		'  make bootstrap                Set up and start a newly generated project' \
		'  make start                    Build and start the development environment' \
		'  make build                    Rebuild the application image' \
		'  make stop                     Stop the development environment' \
		'  make clean                    Remove containers and volumes' \
		'  make shell                    Open a shell in the app container' \
		'  make createsuperuser          Create a Django superuser' \
		'  make test                     Run the Django test suite' \
		'  make manage -- <command>      Run a Django management command' \
		'  make reset-db                 Recreate the local development database'

bootstrap:
	docker compose build app
	docker compose run --rm app python manage.py makemigrations core tagall pages{% if cookiecutter.use_cabinet == 'y' %} cabinet{% endif %}
	docker compose up -d

start:
	docker compose up --build

build:
	docker compose build app

stop:
	docker compose down

clean:
	docker compose down -v --remove-orphans

shell:
	docker compose exec app bash

createsuperuser:
	docker compose exec app python manage.py createsuperuser

test:
	docker compose exec -e DJANGO_SETTINGS_MODULE=core.settings.test app python manage.py test

# drops and recreates the local dev database
reset-db:
	docker compose exec -T app python manage.py dbshell < bin/drop_database.sql
	docker compose exec app python manage.py migrate

endif

# usage: make manage -- migrate
manage:
	docker compose exec app python manage.py $(MANAGE_ARGS)
