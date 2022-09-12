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
        '--clean',
        dest='clean',
        required=False,
        action='store_true',
        help='removes docker containers and volumes')
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
        help='creates a superuser account'
    )
    parser.add_argument(
        '--manage',
        dest='management_command',
        required=False,
        help='executes the given management command')

    parser.add_argument(
        '--remote',
        dest='remote_command',
        required=False,
        help='executes remote commands',
        choices=('setup', 'createReleaseArchive', 'log', 'deploy', 'rollback', 'getRemoteRevision', 'dumpDbSnapshot', 'loadDbSnapshot', 'loadDb', 'offline', 'online', 'reloadServer', 'restartUwsgi', 'restart' ),)

    if complete_enabled:
        argcomplete.autocomplete(parser)
    args = vars(parser.parse_args())

    # functions
    def manage_remote_command(cmd):
        if cmd == 'setup':
            os.system("docker-compose -f docker-compose.yml exec app bash -c \"source ../../venv/bin/activate && ../bin/ansible_remote\"")
        else: # fabric stuff
            os.system("docker-compose -f docker-compose.yml exec app bash -c \"source ../../venv/bin/activate && fab production %s\"" % cmd)

    # options parsing
    if args['start']:
        os.system("docker-compose -f docker-compose.yml up")
    elif args['clean']:
        os.system("docker container stop {{cookiecutter.repo_name}}_app")
        os.system("docker container stop {{cookiecutter.repo_name}}_postgres")
        os.system("docker container rm {{cookiecutter.repo_name}}_app")
        os.system("docker container rm {{cookiecutter.repo_name}}_postgres")
        os.system("docker volume rm {{cookiecutter.repo_name}}_app")
        os.system("docker volume rm {{cookiecutter.repo_name}}_db-data")
        os.system("docker volume rm {{cookiecutter.repo_name}}_virtualenv")
    elif args['open_shell']:
        os.system("docker-compose -f docker-compose.yml exec app bash")
    elif args['createsuperuser']:
        os.system("docker-compose -f docker-compose.yml exec app bash -c \"source ../../venv/bin/activate && python manage.py createsuperuser\"")
    elif args['management_command']:
        os.system(
            "docker-compose -f docker-compose.yml exec app bash -c \"source ../../venv/bin/activate && python manage.py %s\"" % args['management_command']
        )
    elif args['remote_command']:
        manage_remote_command(args['remote_command'])
