"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.urls import path, re_path, include
from baton.autodiscover import admin
from django.conf import settings
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve
from django.contrib.sitemaps.views import sitemap
from pages.sitemap import PageSitemap
{% if cookiecutter.use_translations == 'y' %}
from django.conf.urls.i18n import i18n_patterns
{% endif %}

sitemaps = {
    'pages': PageSitemap,
    # add here other sitemaps
}

urlpatterns = [
    # sitemap
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
    ),
    
    # robots
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),
]


# User-facing URL patterns that can be translated
translatable_urlpatterns = [
    # browser reload
    path("__reload__/", include("django_browser_reload.urls")),
    # admin
    path('admin/', admin.site.urls),
    path('baton/', include('baton.urls')),
    # ckeditor uploader
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # taggit autosuggest
    path("taggit_autosuggest/", include("taggit_autosuggest.urls")),
    {% if cookiecutter.use_filer == 'y' %}
    # filer
    path('filer/', include('filer.urls')),
    {% endif %}

    # home
    path('',TemplateView.as_view(template_name='home.html'), name='home'),
    # pages
    path("p/", include("pages.urls")),
    # search
    path('search/', include('search_app.urls')),
]

{% if cookiecutter.use_translations == 'y' %}
urlpatterns += i18n_patterns(
    *translatable_urlpatterns
)
{% else %}
urlpatterns += translatable_urlpatterns
{% endif %}


if settings.DEBUG:
    # Serve media files from MEDIA_ROOT
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Django Debug Toolbar
    urlpatterns = [
        path('__debug__/', include('debug_toolbar.urls')),
    ] + urlpatterns