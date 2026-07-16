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
from tagall.views import TagallCreateTagsView
{% if cookiecutter.use_cabinet == 'y' %}
from cabinet.views import editor_js_image_upload
{% endif %}
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
    path("baton/create-tags/", TagallCreateTagsView.as_view(), name="baton-create-tags"),
    path('baton/', include('baton.urls')),
    {% if cookiecutter.use_cabinet == 'y' %}
    path('editor-js/editor-js-image-upload/', editor_js_image_upload, name='editor_js_image_upload'),
    {% endif %}
    path('editor-js/', include('editor_js.urls')),
    {% if cookiecutter.use_cabinet == 'y' %}
    # cabinet
    path("cabinet/", include("cabinet.urls", namespace="cabinet")),
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


# Serve uploaded media through Django during local development. In production,
# static() registers no route because DEBUG is false; the internal Nginx
# container serves the shared media volume directly.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # Django Debug Toolbar
    urlpatterns = [
        path('__debug__/', include('debug_toolbar.urls')),
    ] + urlpatterns
