from django.urls import path, re_path

from . import views

app_name = "pages"
urlpatterns = [
    path("rss-feed-preview/<int:page_content_id>/", views.page_content_rss_feed_preview, name="page-rss-feed-preview"),
    path("rss-feed/<int:page_content_id>/", views.page_content_rss_feed_content, name="page-rss-feed-content"),
    re_path(r"(?P<url>.*)/$", views.page, name="page"),
]
