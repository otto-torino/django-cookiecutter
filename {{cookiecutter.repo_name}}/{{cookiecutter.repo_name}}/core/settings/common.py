# -*- coding: utf-8 -*-
"""
Django settings for {{ cookiecutter.project_name }} project.
"""

from datetime import datetime
from os import getenv
from pathlib import Path
from dotenv import load_dotenv
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = getenv('SECRET_KEY')

# ADMINS
ADMINS = (
    ('{{ cookiecutter.author }}', '{{ cookiecutter.email }}'),
)

# AUTH USER
AUTH_USER_MODEL = 'core.User'

# SITE
SITE_ID = 1

# MAIL
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25

# Optional cookie-consent widget. Empty by default, so no external asset or
# placeholder URL is rendered until an environment provides a real code.
COOKIERULEZ_WIDGET_CODE = getenv('COOKIERULEZ_WIDGET_CODE', '').strip()

# REMOTE RSS FEEDS
RSS_FEED_TIMEOUT = 5
RSS_FEED_MAX_BYTES = 2 * 1024 * 1024
RSS_FEED_CACHE_TIMEOUT = 300
RSS_FEED_MAX_REDIRECTS = 3

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': getenv('DB_HOST'),
        'PORT': getenv('DB_PORT'),
        'NAME': getenv('DB_NAME'),
        'USER': getenv('DB_USER'),
        'PASSWORD': getenv('DB_PASSWORD'),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# APPLICATIONS
INSTALLED_APPS = (
    # Initial apps
    'core',
    'tagall',
    {% if cookiecutter.use_translations == 'y' %}'modeltranslation',{% endif %}
    'baton',

    # Django default apps
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    # Third party apps
    'editor_js',
    'django_extensions',
    'compressor',
    'preferences_utils',
    'subject_imagefield',
    "colorfield",
    'tailwind',
    'django_web_components',
    {% if cookiecutter.use_cabinet == 'y' %}'cabinet',{% endif %}
    'django_cleanup',
    {% if cookiecutter.use_sorl_thumbnail == 'y' %}'sorl.thumbnail',{% endif %}
    'lineup',

    # Custom apps
    'pages',
    'theme',
    'search_app',

    'baton.autodiscover',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    {% if cookiecutter.use_translations == 'y' %}
    'django.middleware.locale.LocaleMiddleware',
    {% endif %}
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': False,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'preferences_utils.context_processors.preferences.pref',
                'core.context_processors.debug',
                'core.context_processors.absurl',
                'core.context_processors.cookierulez',
            ],
            "builtins": [
                "django_web_components.templatetags.components",
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# THEME
TAILWIND_APP_NAME = 'theme'
NPM_BIN_PATH = '/usr/local/bin/npm'

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = '{{ cookiecutter.default_language}}'
{% if cookiecutter.default_language == 'it' %}LANGUAGES = (
    ("it", "italian"),
){% else %}LANGUAGES = (
    ("en", "english"),
){% endif %}
{% if cookiecutter.use_translations == 'y' %}MODELTRANSLATION_DEFAULT_LANGUAGE = "{{ cookiecutter.default_language}}"{% endif %}

TIME_ZONE = '{{ cookiecutter.timezone }}'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
STATIC_URL = '/static/'

# Uploaded files
MEDIA_URL = '/media/'
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# ADMIN


def _current_site_copyright():
    """Build the admin copyright from the current Site (django.contrib.sites).

    Evaluated lazily (at render time, not settings-import time) so it reads the
    live Site row from the DB - this way the domain/name differs automatically
    between environments (staging vs production) without baking it into settings.
    Falls back to the project name if the sites table isn't available yet
    (e.g. during collectstatic at image build, before migrations run).
    """
    try:
        from django.contrib.sites.models import Site
        name = Site.objects.get_current().name
    except Exception:
        name = '{{ cookiecutter.project_name }}'
    return '© %d %s' % (datetime.now().year, name)


current_site_copyright = lazy(_current_site_copyright, str)

BATON = {
    'SITE_HEADER': '{{ cookiecutter.project_name }}',
    'SITE_TITLE': '{{ cookiecutter.project_name }}',
    'INDEX_TITLE': 'Site administration',
    'MENU': (
        {'type': 'title', 'label': 'System',  'apps': ('auth', 'sites', 'core', ), 'icon': 'desktop_windows', 'children': [

            {'type': 'model', 'app': 'core', 'name': 'user', 'label': 'Users',},
            {'type': 'model', 'app': 'auth', 'name': 'group', 'label': 'Groups',},
            {'type': 'model', 'app': 'sites', 'name': 'site', 'label': 'Sites',},
            {'type': 'model', 'app': 'core', 'name': 'preferences', 'label': 'Settings',},
        ]},
        {% if cookiecutter.use_cabinet == 'y' %}
            {'type': 'title', 'label': 'Resources',  'apps': ('cabinet', ), 'icon': 'storage', 'children': [
                {'type': 'model', 'app': 'cabinet', 'name': 'file', 'label': _('File manager'),},
            ]},
        {% endif %}
        {'type': 'title', 'label': 'Navigation',  'apps': ('lineup', ), 'icon': 'menu', 'children': [
            {'type': 'model', 'app': 'lineup', 'name': 'menuitem', 'label': 'Menu',},
        ]},
         {'type': 'title', 'label': 'Contents',  'apps': ('pages', 'tagall', ), 'icon': 'description', 'default_open': True, 'children': [
            {'type': 'model', 'app': 'pages', 'name': 'page', 'label': 'Pages',},
            {'type': 'model', 'app': 'tagall', 'name': 'tag', 'label': 'Tags',},
        ]},
    ),
    'COPYRIGHT': current_site_copyright(),
    'SUPPORT_HREF': getenv('SUPPORT_HREF', 'mailto:mail@otto.srl'),
    'POWERED_BY': '<a href="https://www.otto.srl">Otto</a>'
}

{% if cookiecutter.use_cabinet == 'y' %}
CABINET_FILE_MODEL = "cabinet.File"
{% endif %}

# EDITOR.JS
EDITOR_JS = {
    "CSS_FILES": [
        "core/src/css/editor_js.css",
    ],
}

# LOGGING

LOGGING_DEFAULT = {
    'handlers': ['console', 'file'],
    'level': 'DEBUG',
    'propagate': True,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s' # noqa
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
       'null': {
            'level': 'DEBUG',
            'class':'logging.NullHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        # configure the log to be rotated daily
        # see https://docs.python.org/2.7/library/logging.handlers.html#logging.handlers.TimedRotatingFileHandler
        'file': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'concurrent_log_handler.ConcurrentTimedRotatingFileHandler',
            'when':     'midnight',
        },

        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
       'django.template': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'console', 'file',],
            'level': 'ERROR',
            'propagate': False,
        },
        # http://stackoverflow.com/questions/7768027/turn-off-sql-logging-while-keeping-settings-debug
       'django.db.backends': {
            'handlers': ['null'],  # Quiet by default!
            'propagate': False,
            'level':'DEBUG',
        },
       'sorl.thumbnail': {
            'handlers': ['null'],  # Quiet by default!
            'propagate': False,
            'level':'DEBUG',
        },
        'core': LOGGING_DEFAULT,
        '':                             LOGGING_DEFAULT,# root logger
    },
}
