from django import template
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

register = template.Library()

@register.filter()
def absurl(url):
    request = None
    return "".join(["http%s://" % ("s" if not settings.DEBUG else ""), get_current_site(request).domain, str(url)])
