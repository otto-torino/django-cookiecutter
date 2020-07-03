#!/usr/bin/python
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-

import argparse
import os

try:
    import argcomplete
    complete_enabled = True
except Exception:
    print('''
          If you want a better cli experience, install argcomplete
          and activate global completion,
          see https://kislyuk.github.io/argcomplete/'''
          )
    complete_enabled = False

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
    parser.add_argument(
        '--manage',
        dest='management_command',
        required=False,
        help='executes the given management command')

    if complete_enabled:
        argcomplete.autocomplete(parser)
    args = vars(parser.parse_args())

    if args['start']:
        os.system("docker-compose -f docker-compose.yml up")
    elif args['open_shell']:
        os.system("docker-compose -f docker-compose.yml exec app bash")
    elif args['createsuperuser']:
        os.system("docker-compose -f docker-compose.yml exec app bash -c \"source ../../venv/bin/activate && export DJANGO_SUPERUSER_PASSWORD=admin && python manage.py createsuperuser --no-input --username admin --email kkk@otto.to.it\"")
    elif args['management_command']:
        os.system(
            "docker-compose -f docker-compose.yml exec app bash -c \"source ../../venv/bin/activate && python manage.py %s\"" % args['management_command']
        )
