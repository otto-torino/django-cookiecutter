'''This module sets the configuration for production, running fully inside Docker
behind the host's Nginx reverse proxy, which terminates TLS.

'''
from .common import *

DEBUG = False
THUMBNAIL_DEBUG = False

# ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS are supplied per-environment via the
# GitHub Environment variables and are mandatory at deploy time: the Compose
# files declare them as ${...:?} and the deploy workflow aborts if unset, so the
# real domain always arrives via the env var. The 'example.com' default here is
# only a harmless placeholder for build-time commands (collectstatic /
# compilemessages) that run production settings without serving requests.
ALLOWED_HOSTS = [
    host.strip()
    for host in getenv('ALLOWED_HOSTS', 'example.com').split(',')
    if host.strip()
]

# The host's Nginx terminates TLS and proxies to the loopback-bound container.
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in getenv(
        'CSRF_TRUSTED_ORIGINS', 'https://example.com'
    ).split(',')
    if origin.strip()
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# HTTPS is terminated by the host's Nginx, which forwards X-Forwarded-Proto.
# Start HSTS with a short lifetime; increase it only after HTTPS has proved
# reliable. includeSubDomains and preload intentionally remain disabled.
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(getenv('SECURE_HSTS_SECONDS', '3600'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Paths are container-absolute (see compose/app/Dockerfile.production's WORKDIR /app),
# not host paths - the app never runs on bare metal in production.
STATIC_ROOT = getenv('STATIC_ROOT', '/app/static')
MEDIA_ROOT = getenv('MEDIA_ROOT', '/app/media')

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
    "core/src/css/editor_js.css",
]
