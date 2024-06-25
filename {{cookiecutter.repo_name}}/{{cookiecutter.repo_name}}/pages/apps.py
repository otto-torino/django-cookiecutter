# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class PagesConfig(AppConfig):
    name = 'pages'
    verbose_name = "Pagine"

    def ready(self):
        from . import components  # noqa
