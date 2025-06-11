from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.views.decorators.csrf import csrf_protect

from pages.handlers import consume_rss_feed

from .models import Page, PageContentRssFeed

DEFAULT_TEMPLATE = "pages/default.html"

# This view is called from PageFallbackMiddleware.process_response
# when a 404 is raised, which often means CsrfViewMiddleware.process_view
# has not been called even if CsrfViewMiddleware is installed. So we need
# to use @csrf_protect, in case the template needs {% raw %}{% csrf_token %}{% endraw %}.
# However, we can't just wrap this view; if no matching page exists,
# or a redirect is required for authentication, the 404 needs to be returned
# without any CSRF checks. Therefore, we only
# CSRF protect the internal implementation.


def page(request, url):
    """
    Public interface to the page view.

    Models: `pages.page`
    Templates: Uses the template defined by the ``template_name`` field,
        or :template:`pages/default.html` if template_name is not defined.
    Context:
        page
            `pages.page` object
    """
    url = f"/{url.strip('/')}/"
    site_id = get_current_site(request).id
    p = get_object_or_404(Page, url=url, sites=site_id)
    return render_page(request, p)


@csrf_protect
def render_page(request, p):
    """
    Internal interface to the page view.
    """
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if p.registration_required and not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(request.path)
    # If page is not pusblished, raise 404
    if not p.status == Page.PUBLISHED:
        raise Http404
    if p.template_name:
        template = loader.select_template((p.template_name, DEFAULT_TEMPLATE))
    else:
        template = loader.get_template(DEFAULT_TEMPLATE)
    date = p.modified
    for block in p.content_blocks.for_content():
        if block.modified > date:
            date = block.modified
    response = HttpResponse(template.render({"page": p, "updated": date}, request))
    return response


def page_content_rss_feed_preview(request, page_content_id):
    page_content = get_object_or_404(PageContentRssFeed, id=page_content_id)
    feed = consume_rss_feed(page_content.rss_feed_url)
    ctx = {
        "entries": feed.entries[: page_content.num_items],
    }
    return render(
        request,
        "admin/pages/page_content_rss_feed/rss_feed_admin.html",
        ctx,
    )


def page_content_rss_feed_content(request, page_content_id):
    page_content = get_object_or_404(PageContentRssFeed, id=page_content_id)
    feed = consume_rss_feed(page_content.rss_feed_url)
    ctx = {
        "entries": feed.entries[: page_content.num_items],
    }
    return render(
        request,
        "pages/page_content_rss_feed_content.html",
        ctx,
    )
