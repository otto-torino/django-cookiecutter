'''This module sets the configuration for a local development

'''
from .common import *

DEBUG = False
THUMBNAIL_DEBUG = False

ALLOWED_HOSTS = ['{{ cookiecutter.domain }}',]

STATIC_ROOT = '{{cookiecutter.webapp_dir}}/static'
MEDIA_ROOT = '{{cookiecutter.webapp_dir}}/media'
LOGGING['handlers']['file']['filename'] = '{{cookiecutter.webapp_dir}}/logs/{{cookiecutter.repo_name}}.log'

# EDITOR.JS
EDITOR_JS["CSS_FILES"] = [
    "css/dist/styles.css",
    "{{ cookiecutter.core_name }}/src/css/editor_js.css",
]
