.PHONY: start stop clean shell createsuperuser manage reset-db

start:
	docker compose up

stop:
	docker compose down

clean:
	docker compose down -v --remove-orphans

shell:
	docker compose exec app bash

createsuperuser:
	docker compose exec app python manage.py createsuperuser

# usage: make manage cmd="migrate"
manage:
	docker compose exec app python manage.py $(cmd)

# drops and recreates the local dev database
reset-db:
	docker compose exec -T app python manage.py dbshell < bin/drop_database.sql
