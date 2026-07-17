.PHONY: start build stop clean shell createsuperuser manage reset-db

ifeq (manage,$(firstword $(MAKECMDGOALS)))
MANAGE_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
.PHONY: $(MANAGE_ARGS)
$(MANAGE_ARGS):
	@:

else

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

# drops and recreates the local dev database
reset-db:
	docker compose exec -T app python manage.py dbshell < bin/drop_database.sql
	docker compose exec app python manage.py migrate

endif

# usage: make manage -- migrate
manage:
	docker compose exec app python manage.py $(MANAGE_ARGS)
