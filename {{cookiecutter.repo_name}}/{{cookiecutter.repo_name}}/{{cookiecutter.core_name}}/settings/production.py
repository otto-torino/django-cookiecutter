'''This module sets the configuration for production, running fully inside Docker
behind a Traefik reverse proxy that terminates TLS.

'''
from .common import *

DEBUG = False
THUMBNAIL_DEBUG = False

ALLOWED_HOSTS = ['{{ cookiecutter.domain }}',]

# Traefik terminates TLS and proxies to the app container over plain HTTP.
CSRF_TRUSTED_ORIGINS = ['https://{{ cookiecutter.domain }}']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Paths are container-absolute (see compose/app/Dockerfile.production's WORKDIR /app),
# not host paths - the app never runs on bare metal in production.
STATIC_ROOT = '/app/static'
MEDIA_ROOT = '/app/media'

# Log to stdout only: the container runtime (docker logs / CI) captures it, no
# host log directory or rotation needed. Every logger below references the
# 'file' handler by name, so redefining it in place routes them all to stdout
# without touching per-logger handler lists (e.g. django.request still also
# mails admins via 'mail_admins').
LOGGING['handlers']['file'] = LOGGING['handlers']['console']

# WhiteNoise must sit directly after SecurityMiddleware.
_security_middleware = 'django.middleware.security.SecurityMiddleware'
_idx = list(MIDDLEWARE).index(_security_middleware) + 1
MIDDLEWARE = MIDDLEWARE[:_idx] + ('whitenoise.middleware.WhiteNoiseMiddleware',) + MIDDLEWARE[_idx:]

# Not the hashed/manifest variant: some vendored static assets (e.g. swiper)
# reference sourcemaps that aren't shipped alongside them, and Django's hashed
# storage rewrites (and hard-fails collectstatic over) such missing references.
# Plain compression avoids that whole class of problem, at the cost of not having
# content-hashed cache-busting filenames.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# EDITOR.JS
EDITOR_JS["CSS_FILES"] = [
    "css/dist/styles.css",
    "{{ cookiecutter.core_name }}/src/css/editor_js.css",
]
