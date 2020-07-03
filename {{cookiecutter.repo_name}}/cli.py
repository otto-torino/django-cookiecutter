#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Otto Web Application CLI')
    parser.add_argument(
        '--start',
        dest='start',
        required=False,
        action='store_true',
        help='starts the environment')
    parser.add_argument(
        '--runserver',
        dest='runserver',
        required=False,
        action='store_true',
        help='execs a django runserver command')
    parser.add_argument(
        '--shell',
        dest='open_shell',
        required=False,
        action='store_true',
        help='opens a shell in the app container'
    )
    parser.add_argument(
        '--createsuperuser',
        dest='createsuperuser',
        required=False,
        action='store_true',
        help='creates an admin:admin superuser account'
    )
    args = vars(parser.parse_args())

    if args['start']:
        os.system("docker-compose -f docker-compose.yml up")
    elif args['open_shell']:
        os.system("docker-compose -f docker-compose.yml exec app bash")
    elif args['runserver']:
        os.system("docker-compose -f docker-compose.yml exec app -w /home/app/{{ cookiecutter.repo_name }}/{{ cookiecutter.repo_name }} bash -c \"source ../../venv/bin/activate && python manage.py runserver\"")
    elif args['createsuperuser']:
        os.system("docker-compose -f docker-compose.yml exec app -w /home/app/{{ cookiecutter.repo_name }}/{{ cookiecutter.repo_name }} bash -c \"source ../../venv/bin/activate && export DJANGO_SUPERUSER_PASSWORD=admin && python manage.py createsuperuser --no-input --username admin --email kkk@otto.to.it\"")

