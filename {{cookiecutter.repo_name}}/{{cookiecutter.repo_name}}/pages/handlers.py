import hashlib
import http.client
import ipaddress
import socket
import ssl
from urllib.parse import urljoin, urlsplit

import feedparser
from django.conf import settings
from django.core.cache import cache
from django.utils.html import strip_tags


class FeedFetchError(Exception):
    """Raised when an RSS feed cannot be fetched safely."""


class UnsafeFeedURLError(FeedFetchError):
    """Raised when an RSS URL could reach a non-public network."""


class _PinnedHTTPConnection(http.client.HTTPConnection):
    def __init__(self, host, port, address, *, timeout):
        super().__init__(host, port, timeout=timeout)
        self.address = address

    def connect(self):
        self.sock = socket.create_connection(
            (self.address, self.port),
            self.timeout,
            self.source_address,
        )


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host, port, address, *, timeout):
        super().__init__(
            host,
            port,
            timeout=timeout,
            context=ssl.create_default_context(),
        )
        self.address = address

    def connect(self):
        self.sock = socket.create_connection(
            (self.address, self.port),
            self.timeout,
            self.source_address,
        )
        self.sock = self._context.wrap_socket(self.sock, server_hostname=self.host)


def _resolve_public_addresses(hostname, port):
    try:
        address_info = socket.getaddrinfo(
            hostname,
            port,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise FeedFetchError("The feed hostname could not be resolved.") from exc

    addresses = []
    for *_, socket_address in address_info:
        address = socket_address[0]
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as exc:
            raise UnsafeFeedURLError(
                "The feed resolved to an invalid address."
            ) from exc
        if not ip.is_global:
            raise UnsafeFeedURLError(
                "RSS feeds must not resolve to private or reserved addresses."
            )
        if address not in addresses:
            addresses.append(address)

    if not addresses:
        raise FeedFetchError("The feed hostname did not resolve to an address.")
    return addresses


def validate_feed_url(url):
    """Validate an RSS URL and return its parsed URL and pinned public IPs."""
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except (TypeError, ValueError) as exc:
        raise UnsafeFeedURLError("The RSS feed URL is invalid.") from exc

    if parsed.scheme not in {"http", "https"}:
        raise UnsafeFeedURLError("RSS feeds must use HTTP or HTTPS.")
    if not parsed.hostname or parsed.username or parsed.password:
        raise UnsafeFeedURLError(
            "RSS feed URLs must contain a hostname and no credentials."
        )

    port = port or (443 if parsed.scheme == "https" else 80)
    addresses = _resolve_public_addresses(parsed.hostname, port)
    return parsed, port, addresses


def _request_feed(url):
    parsed, port, addresses = validate_feed_url(url)
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"

    timeout = settings.RSS_FEED_TIMEOUT
    max_bytes = settings.RSS_FEED_MAX_BYTES
    last_error = None

    for address in addresses:
        connection_class = (
            _PinnedHTTPSConnection
            if parsed.scheme == "https"
            else _PinnedHTTPConnection
        )
        connection = connection_class(
            parsed.hostname,
            port,
            address,
            timeout=timeout,
        )
        try:
            connection.request(
                "GET",
                path,
                headers={
                    "Accept": (
                        "application/atom+xml, application/rss+xml, "
                        "application/xml, text/xml"
                    ),
                    "User-Agent": "Django RSS feed reader/1.0",
                },
            )
            response = connection.getresponse()
            content_length = response.getheader("Content-Length")
            if content_length and int(content_length) > max_bytes:
                raise FeedFetchError("The RSS feed response is too large.")
            body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                raise FeedFetchError("The RSS feed response is too large.")
            return response.status, response.getheader("Location"), body
        except (OSError, http.client.HTTPException, ValueError) as exc:
            last_error = exc
        finally:
            connection.close()

    raise FeedFetchError("The RSS feed could not be downloaded.") from last_error


def _download_feed(url):
    current_url = url
    redirect_statuses = {301, 302, 303, 307, 308}

    for redirect_count in range(settings.RSS_FEED_MAX_REDIRECTS + 1):
        status, location, body = _request_feed(current_url)
        if status in redirect_statuses:
            if not location or redirect_count == settings.RSS_FEED_MAX_REDIRECTS:
                raise FeedFetchError("The RSS feed redirected too many times.")
            current_url = urljoin(current_url, location)
            continue
        if not 200 <= status < 300:
            raise FeedFetchError(f"The RSS feed returned HTTP {status}.")
        return body

    raise FeedFetchError("The RSS feed redirected too many times.")


def _safe_external_url(url):
    if not url:
        return ""
    try:
        parsed = urlsplit(url)
    except (TypeError, ValueError):
        return ""
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username
        or parsed.password
    ):
        return ""
    return url


def _sanitize_entries(entries):
    sanitized = []
    for entry in entries:
        thumbnails = entry.get("media_thumbnail") or []
        thumbnail_url = thumbnails[0].get("url", "") if thumbnails else ""
        sanitized.append(
            {
                "title": strip_tags(str(entry.get("title", ""))),
                "summary": strip_tags(str(entry.get("summary", ""))),
                "link": _safe_external_url(entry.get("link", "")),
                "thumbnail_url": _safe_external_url(thumbnail_url),
                "published_parsed": entry.get("published_parsed"),
            }
        )
    return sanitized


def consume_rss_feed(url):
    """Fetch, cache, parse and sanitize an RSS feed."""
    cache_key = f"pages:rss:{hashlib.sha256(url.encode()).hexdigest()}"
    payload = cache.get(cache_key)
    downloaded = payload is None
    if payload is None:
        payload = _download_feed(url)

    feed = feedparser.parse(payload)
    if feed.bozo and not feed.entries:
        raise FeedFetchError("The RSS response is not a valid feed.")
    if downloaded:
        cache.set(cache_key, payload, settings.RSS_FEED_CACHE_TIMEOUT)
    return _sanitize_entries(feed.entries)
