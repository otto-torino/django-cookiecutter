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
    'django_browser_reload',
)

MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
) + MIDDLEWARE

TEMPLATES[0]['OPTIONS']['debug'] = True

# MAIL
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'mailhog'
EMAIL_PORT = 1025

# EDITOR.JS
EDITOR_JS["CSS_FILES"] = [
    "core/src/scss/styles.css",
    "core/src/css/editor_js.css",
]

# DEBUG_TOOLBAR
JQUERY_URL = ''

def show_toolbar(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return False
    return True

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}
