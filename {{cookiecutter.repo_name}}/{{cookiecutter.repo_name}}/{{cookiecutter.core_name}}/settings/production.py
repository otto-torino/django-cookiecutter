'''This module sets the configuration for a local development

'''
from .common import *

DEBUG = False
THUMBNAIL_DEBUG = False

ALLOWED_HOSTS = ['{{ cookiecutter.domain }}',]

STATIC_ROOT = '{{cookiecutter.webapp_dir}}/static'
MEDIA_ROOT = '{{cookiecutter.webapp_dir}}/media'
LOGGING['handlers']['file']['filename'] = '{{cookiecutter.webapp_dir}}/logs/{{cookiecutter.repo_name}}.log'

# CKEDITOR
CKEDITOR_CONFIGS['default']['contentsCss'] = [
    STATIC_URL + '{{ cookiecutter.core_name }}/css/vendor.min.css',
    STATIC_URL + '{{ cookiecutter.core_name }}/src/vendor/semantic-ui/semantic.min.css',
    STATIC_URL + '{{ cookiecutter.core_name }}/css/core.min.css',
    STATIC_URL + '{{ cookiecutter.core_name }}/src/css/ckeditor.css']
