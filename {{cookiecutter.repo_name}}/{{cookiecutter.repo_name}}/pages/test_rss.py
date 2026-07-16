import socket
from unittest.mock import MagicMock, call, patch
from urllib.parse import urlsplit

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .handlers import (
    FeedFetchError,
    UnsafeFeedURLError,
    _download_feed,
    _sanitize_entries,
    consume_rss_feed,
    validate_feed_url,
)
from .models import Page, PageContentRssFeed


class RSSFeedHandlerTests(TestCase):
    def tearDown(self):
        cache.clear()

    @patch("pages.handlers.socket.getaddrinfo")
    def test_feed_url_accepts_only_public_addresses(self, getaddrinfo):
        getaddrinfo.return_value = [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                ("8.8.8.8", 443),
            )
        ]

        parsed, port, addresses = validate_feed_url("https://example.com/feed")

        self.assertEqual(parsed.hostname, "example.com")
        self.assertEqual(port, 443)
        self.assertEqual(addresses, ["8.8.8.8"])

    @patch("pages.handlers.socket.getaddrinfo")
    def test_feed_url_rejects_private_addresses(self, getaddrinfo):
        getaddrinfo.return_value = [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                ("8.8.8.8", 80),
            ),
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                ("127.0.0.1", 80),
            )
        ]

        with self.assertRaises(UnsafeFeedURLError):
            validate_feed_url("http://example.com/feed")

    def test_feed_url_rejects_unsafe_schemes_and_credentials(self):
        unsafe_urls = (
            "file:///etc/passwd",
            "ftp://example.com/feed",
            "https://user:password@example.com/feed",
        )

        for url in unsafe_urls:
            with self.subTest(url=url), self.assertRaises(UnsafeFeedURLError):
                validate_feed_url(url)

    @override_settings(
        RSS_FEED_MAX_REDIRECTS=3,
        RSS_FEED_TIMEOUT=5,
        RSS_FEED_MAX_BYTES=1024,
    )
    @patch("pages.handlers._PinnedHTTPConnection")
    @patch("pages.handlers.validate_feed_url")
    def test_redirect_target_is_resolved_and_validated_again(
        self,
        validate,
        connection_class,
    ):
        source_url = "http://example.com/feed"
        target_url = "http://feeds.example.net/rss"
        validate.side_effect = [
            (urlsplit(source_url), 80, ["8.8.8.8"]),
            (urlsplit(target_url), 80, ["1.1.1.1"]),
        ]
        redirect_response = MagicMock(status=302)
        redirect_response.getheader.side_effect = lambda name: (
            target_url if name == "Location" else None
        )
        redirect_response.read.return_value = b""
        success_response = MagicMock(status=200)
        success_response.getheader.return_value = None
        success_response.read.return_value = b"feed"
        redirect_connection = MagicMock()
        redirect_connection.getresponse.return_value = redirect_response
        success_connection = MagicMock()
        success_connection.getresponse.return_value = success_response
        connection_class.side_effect = [redirect_connection, success_connection]

        payload = _download_feed(source_url)

        self.assertEqual(payload, b"feed")
        self.assertEqual(validate.call_args_list, [call(source_url), call(target_url)])
        self.assertEqual(
            connection_class.call_args_list,
            [
                call("example.com", 80, "8.8.8.8", timeout=5),
                call("feeds.example.net", 80, "1.1.1.1", timeout=5),
            ],
        )

    def test_feed_entries_are_rendered_as_plain_text_with_safe_urls(self):
        entries = _sanitize_entries(
            [
                {
                    "title": "<b>Title</b>",
                    "summary": '<script>alert("xss")</script><p>Summary</p>',
                    "link": "javascript:alert(1)",
                    "media_thumbnail": [{"url": "data:text/html,danger"}],
                }
            ]
        )

        self.assertEqual(entries[0]["title"], "Title")
        self.assertNotIn("<", entries[0]["summary"])
        self.assertEqual(entries[0]["link"], "")
        self.assertEqual(entries[0]["thumbnail_url"], "")

    @override_settings(RSS_FEED_CACHE_TIMEOUT=300)
    @patch("pages.handlers.feedparser.parse")
    @patch("pages.handlers._download_feed")
    def test_successful_feed_download_is_cached(self, download, parse):
        download.return_value = b"feed"
        parse.return_value.bozo = False
        parse.return_value.entries = []

        consume_rss_feed("https://example.com/feed")
        consume_rss_feed("https://example.com/feed")

        download.assert_called_once_with("https://example.com/feed")

    @patch("pages.handlers.feedparser.parse")
    @patch("pages.handlers._download_feed")
    def test_invalid_feed_raises_a_controlled_error(self, download, parse):
        download.return_value = b"not a feed"
        parse.return_value.bozo = True
        parse.return_value.entries = []

        with self.assertRaises(FeedFetchError):
            consume_rss_feed("https://example.com/invalid")


class RSSFeedViewTests(TestCase):
    def setUp(self):
        self.site = Site.objects.get_current()
        self.site.domain = "testserver"
        self.site.save()
        Site.objects.clear_cache()
        self.page = Page.objects.create(
            url="/news/",
            title="News",
            status=Page.PUBLISHED,
        )
        self.page.sites.add(self.site)
        self.block = PageContentRssFeed.objects.create(
            page=self.page,
            content_type=ContentType.objects.get_for_model(PageContentRssFeed),
            name="Feed",
            position=0,
            rss_feed_url="https://example.com/feed.xml",
        )
        self.user = get_user_model().objects.create_user(
            username="user",
            password="password",
        )
        self.staff = get_user_model().objects.create_user(
            username="staff",
            password="password",
            is_staff=True,
        )

    def content_url(self):
        return reverse("pages:page-rss-feed-content", args=[self.block.pk])

    def preview_url(self):
        return reverse("pages:page-rss-feed-preview", args=[self.block.pk])

    @patch("pages.views.consume_rss_feed", return_value=[])
    def test_public_endpoint_inherits_page_access(self, consume):
        response = self.client.get(self.content_url())

        self.assertEqual(response.status_code, 200)
        consume.assert_called_once_with(self.block.rss_feed_url)

    @patch("pages.views.consume_rss_feed", return_value=[])
    def test_public_endpoint_hides_inaccessible_pages(self, consume):
        self.page.registration_required = True
        self.page.save()
        self.page.users.add(self.staff)
        self.client.force_login(self.user)

        response = self.client.get(self.content_url())

        self.assertEqual(response.status_code, 404)
        consume.assert_not_called()

    def test_preview_requires_a_staff_account(self):
        anonymous_response = self.client.get(self.preview_url())
        self.client.force_login(self.user)
        user_response = self.client.get(self.preview_url())

        self.assertEqual(anonymous_response.status_code, 302)
        self.assertEqual(user_response.status_code, 302)

    @patch("pages.views.consume_rss_feed", return_value=[])
    def test_staff_can_open_preview(self, consume):
        self.client.force_login(self.staff)

        response = self.client.get(self.preview_url())

        self.assertEqual(response.status_code, 200)
        consume.assert_called_once_with(self.block.rss_feed_url)

    @patch("pages.views.consume_rss_feed", side_effect=FeedFetchError)
    def test_fetch_errors_are_rendered_safely(self, consume):
        response = self.client.get(self.content_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "RSS feed is temporarily unavailable")
