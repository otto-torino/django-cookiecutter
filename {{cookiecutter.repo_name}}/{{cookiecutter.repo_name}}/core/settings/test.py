"""Settings used by the generated project's automated test suite."""

from .common import *

DEBUG = False
ALLOWED_HOSTS = ["testserver"]

STATIC_ROOT = BASE_DIR / "static-test"
MEDIA_ROOT = BASE_DIR / "media-test"

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Tests must not depend on the local log directory or send error emails.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

# Secure password hashers add no value in isolated automated tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
