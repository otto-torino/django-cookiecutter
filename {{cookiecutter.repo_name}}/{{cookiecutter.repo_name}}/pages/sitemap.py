from django.conf import settings
from django.contrib.sitemaps import Sitemap

from .models import Page


class PageSitemap(Sitemap):
    changefreq = "weekly"
    i18n = True
    alternates = True
    x_default = True

    def items(self):
        return Page.objects.public().for_site(settings.SITE_ID)

    def priority(self, obj):
        return 0.7

    def lastmod(self, obj):
        return obj.modified
