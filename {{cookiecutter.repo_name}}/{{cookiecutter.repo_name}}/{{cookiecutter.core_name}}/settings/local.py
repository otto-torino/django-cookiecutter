'''This module sets the configuration for a local development

'''
from .common import *

DEBUG = True
ALLOWED_HOSTS = []
INTERNAL_IPS = ('127.0.0.1', )  # debug toolbar and tailwind

STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT = BASE_DIR / 'media'
LOGGING['handlers']['file']['filename'] = BASE_DIR / '../logs/{{cookiecutter.repo_name}}.log'

INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE

TEMPLATES[0]['OPTIONS']['debug'] = True

# MAIL
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'mailhog'
EMAIL_PORT = 1025

# CKEDITOR
CKEDITOR_CONFIGS['default']['contentsCss'] = [
    STATIC_URL + '{{ cookiecutter.core_name }}/src/scss/styles.css',
    STATIC_URL + '{{ cookiecutter.core_name }}/src/css/ckeditor.css']

# DEBUG_TOOLBAR
JQUERY_URL = ''

def show_toolbar(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return False
    return True

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}
