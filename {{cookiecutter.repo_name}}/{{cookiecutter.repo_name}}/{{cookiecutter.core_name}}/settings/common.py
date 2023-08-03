# -*- coding: utf-8 -*-
"""
Django settings for {{ cookiecutter.project_name }} project.
"""

from os import getenv
from pathlib import Path
from dotenv import load_dotenv
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
    '{{ cookiecutter.core_name }}',
    {% if cookiecutter.admin == 'django-baton' %}'baton',{% elif cookiecutter.admin == 'django-suit' %}'suit',{% elif cookiecutter.admin == 'django-grappelli' %}'grappelli',{% endif %}
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'ckeditor_uploader',
    'django_user_agents',
    'django_extensions',
    'compressor',
    'tailwind',
    # 'theme',
    'django_browser_reload',
    {% if cookiecutter.use_filer == 'y' %}
    'filer',
    'easy_thumbnails',
    {% endif %}
    'django_cleanup',
    {% if cookiecutter.use_simple_captcha == 'y' %}
    'captcha',
    {% endif %}
    {% if cookiecutter.use_subject_imagefield == 'y' %}
    'subject_imagefield',
    {% endif %}
    {% if cookiecutter.use_sorl_thumbnail == 'y' %}
    'sorl.thumbnail',
    {% endif %}
    {% if cookiecutter.use_disqus == 'y' %}'disqus',{% endif %}
    'taggit',
    'mptt',
    'lineup.apps.LineupConfig',
    'apps.SettingsConfig',
    'pages',
    'constance.backends.database',
    {% if cookiecutter.admin == 'django-baton' %}'baton.autodiscover',{% endif %}
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'pages.middleware.PageFallbackMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
)

ROOT_URLCONF = '{{ cookiecutter.core_name }}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': False,
            'context_processors': [
                'constance.context_processors.config',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                '{{ cookiecutter.core_name }}.context_processors.debug',
                '{{ cookiecutter.core_name }}.context_processors.absurl',
            ],
            'libraries': {
                'sorl_thumbnail': 'sorl.thumbnail.templatetags.thumbnail',
            },
        },
    },
]

WSGI_APPLICATION = '{{ cookiecutter.core_name }}.wsgi.application'

# THEME
TAILWIND_APP_NAME = 'theme'
NPM_BIN_PATH = '/usr/bin/npm'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = '{{ cookiecutter.language_code }}'

TIME_ZONE = '{{ cookiecutter.timezone }}'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# CONSTANCE
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'HIDE_ARCHIVED': (True, _('Hide from admin lists archived records')),
    'SITE_TITLE': ('{{ cookiecutter.project_name }}', _('Site title')),
    'META_TITLE': ('{{ cookiecutter.project_name }}', _('Meta title')),
    'META_DESCRIPTION': ('{{ cookiecutter.project_description }}', _('Meta description')),
    'META_KEYWORDS': ('', _('Meta keywords')),
    'OG_TITLE': ('{{ cookiecutter.project_name }}', _('Open Graph title')),
    'OG_TYPE': ('website', _('Open Graph type')),
    'OG_DESCRIPTION': ('{{ cookiecutter.project_description }}', _('Open Graph description')),
    'OG_IMAGE': ('', _('Open Graph image')),
    'TWITTER_TITLE': ('{{ cookiecutter.project_name }}', _('Twitter title')),
    'TWITTER_DESCRIPTION': ('{{ cookiecutter.project_description }}', _('Twitter description')),
    'TWITTER_CREATOR': ('', _('Twitter creator')),
    'TWITTER_IMAGE': ('', _('Twitter image')),
}

CONSTANCE_CONFIG_FIELDSETS = {
    'SEO': ('SITE_TITLE', 'META_TITLE', 'META_DESCRIPTION', 'META_KEYWORDS', ),
    'Facebook Sharing': ('OG_TITLE', 'OG_TYPE', 'OG_DESCRIPTION',
                            'OG_IMAGE', ),
    'Twitter Sharing': ('TWITTER_TITLE', 'TWITTER_DESCRIPTION',
                           'TWITTER_CREATOR', 'TWITTER_IMAGE', ),
    'Administration': ('HIDE_ARCHIVED', ),
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
STATIC_URL = '/static/'

# Uploaded files
MEDIA_URL = '/media/'
FILE_UPLOAD_PERMISSIONS = 0o644

# Compressor
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

# ADMIN
{% if cookiecutter.admin == 'django-baton' %}
BATON = {
    'SITE_HEADER': '{{ cookiecutter.project_name }}',
    'SITE_TITLE': '{{ cookiecutter.project_name }}',
    'INDEX_TITLE': 'Site administration',
    'MENU': (
        {'type': 'title', 'label': 'System',  'apps': ('auth', 'sites', 'constance', )},
        {'type': 'model', 'app': 'core', 'name': 'user', 'label': 'Users', 'icon':'fa fa-user'},
        {'type': 'model', 'app': 'auth', 'name': 'group', 'label': 'Groups', 'icon':'fa fa-users'},
        {'type': 'model', 'app': 'sites', 'name': 'site', 'label': 'Sites', 'icon':'fa fa-leaf'},
        {'type': 'model', 'app': 'constance', 'name': 'config', 'label': 'Settings', 'icon':'fa fa-cogs'},

        {% if cookiecutter.use_filer == 'y' %}
        {'type': 'title', 'label': 'Resources',  'apps': ('filer', )},
        {'type': 'app', 'name': 'filer', 'label': 'File manager', 'icon':'fa fa-file'},
        {% endif %}

        {'type': 'title', 'label': 'Navigation',  'apps': ('lineup', )},
        {'type': 'model', 'app': 'lineup', 'name': 'menuitem', 'label': 'Menu', 'icon':'fa fa-bars'},

        {'type': 'title', 'label': 'Contents',  'apps': ('pages', )},
        {'type': 'model', 'app': 'pages', 'name': 'page', 'label': 'Pages', 'icon':'fa fa-book'},
    ),
    'COPYRIGHT': '© 2021 {{ cookiecutter.domain }}',
    'SUPPORT_HREF': 'mailto:stefano.contini@otto.to.it',
    'POWERED_BY': '<a href="https://www.otto.to.it">Otto</a>'
}
{% elif cookiecutter.admin == 'django-grappelli' %}
GRAPPELLI_ADMIN_TITLE = '{{ cookiecutter.project_name }} - Amministrazione'
{% endif %}

# TAGGIT
TAGGIT_CASE_INSENSITIVE = True

# CKEDITOR
CKEDITOR_UPLOAD_PATH = 'ckeditor/'
CKEDITOR_JQUERY_URL = ''
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono',
        'toolbar_Basic': [
                ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_Full': [
                ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'], # noqa
                ['NumberedList','BulletedList'],
                ['Link','Unlink','Anchor'],
                '/',
                ['Image', 'Flash', 'Table', 'HorizontalRule'],
                ['TextColor', 'BGColor'],
                ['SpecialChar'], ['PasteFromWord', 'PasteText'], ['Source']
        ],
        'toolbar': 'Full',
        'resize_dir': 'both',
        'resize_minWidth': 300,
        'height': 291,
        'width': '100%',
        'filebrowserWindowWidth': 940,
        'filebrowserWindowHeight': 725,
        'removePlugins': 'stylesheetparser',
        'allowedContent': True,
        'extraAllowedContent': 'iframe[*]',
        'stylesSet': 'core_styles:/static/{{ cookiecutter.core_name }}/src/js/ckeditor_styles.js',
    }
}

{% if cookiecutter.use_disqus == 'y' %}
DISQUS_API_KEY = ''
DISQUS_WEBSITE_SHORTNAME = ''
{% endif %}

{% if cookiecutter.use_filer == 'y' %}
THUMBNAIL_HIGH_RESOLUTION = True
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    #'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)
{% endif %}

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
        '{{ cookiecutter.core_name }}': LOGGING_DEFAULT,
        '':                             LOGGING_DEFAULT,# root logger
    },
}
