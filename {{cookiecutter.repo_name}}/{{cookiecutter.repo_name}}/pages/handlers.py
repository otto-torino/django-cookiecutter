import feedparser

def consume_rss_feed(url):
    feed = feedparser.parse(url)
    return feed
