from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.sites.models import Site
from django.template import Context
from django.test import RequestFactory, TestCase

from .models import Page
from .sitemap import PageSitemap
from .templatetags.pages_tags import PageNode


class PageAccessTests(TestCase):
    def setUp(self):
        self.site = Site.objects.get_current()
        self.site.domain = "testserver"
        self.site.name = "Test"
        self.site.save()
        Site.objects.clear_cache()
        self.other_site = Site.objects.create(domain="other.test", name="Other")
        self.user = get_user_model().objects.create_user(
            username="user",
            password="password",
        )
        self.other_user = get_user_model().objects.create_user(
            username="other",
            password="password",
        )
        self.request_factory = RequestFactory()

    def create_page(
        self,
        url,
        *,
        status=Page.PUBLISHED,
        registration_required=False,
        site=None,
    ):
        page = Page.objects.create(
            url=url,
            title=url.strip("/").title() or "Home",
            status=status,
            registration_required=registration_required,
        )
        page.sites.add(site or self.site)
        return page

    def page_url(self, page):
        prefix = {% if cookiecutter.use_translations == 'y' %}"/{{ cookiecutter.default_language }}"{% else %}""{% endif %}
        return f"{prefix}/p{page.url}"

    def test_public_page_is_available_to_anonymous_users(self):
        page = self.create_page("/public/")

        response = self.client.get(self.page_url(page))

        self.assertEqual(response.status_code, 200)

    def test_restricted_page_without_lists_allows_any_authenticated_user(self):
        page = self.create_page("/members/", registration_required=True)

        anonymous_response = self.client.get(self.page_url(page))
        self.client.force_login(self.user)
        authenticated_response = self.client.get(self.page_url(page))

        self.assertEqual(anonymous_response.status_code, 302)
        self.assertIn("next=", anonymous_response.url)
        self.assertEqual(authenticated_response.status_code, 200)

    def test_user_restriction_allows_only_selected_users(self):
        page = self.create_page("/selected-user/", registration_required=True)
        page.users.add(self.user)

        self.client.force_login(self.user)
        allowed_response = self.client.get(self.page_url(page))
        self.client.force_login(self.other_user)
        denied_response = self.client.get(self.page_url(page))

        self.assertEqual(allowed_response.status_code, 200)
        self.assertEqual(denied_response.status_code, 404)

    def test_group_restriction_allows_group_members(self):
        group = Group.objects.create(name="Members")
        self.user.groups.add(group)
        page = self.create_page("/selected-group/", registration_required=True)
        page.groups.add(group)

        self.assertTrue(page.is_accessible_by(self.user))
        self.assertFalse(page.is_accessible_by(self.other_user))

    def test_editor_can_preview_drafts_and_restricted_pages(self):
        permission = Permission.objects.get(
            codename="change_page",
            content_type__app_label="pages",
        )
        self.user.user_permissions.add(permission)
        page = self.create_page(
            "/draft/",
            status=Page.DRAFT,
            registration_required=True,
        )
        page.users.add(self.other_user)

        self.client.force_login(self.user)
        response = self.client.get(self.page_url(page))

        self.assertEqual(response.status_code, 200)

    def test_accessible_queryset_filters_status_site_and_restrictions(self):
        public = self.create_page("/public/")
        selected = self.create_page("/selected/", registration_required=True)
        selected.users.add(self.user)
        self.create_page("/other-user/", registration_required=True).users.add(
            self.other_user
        )
        self.create_page("/draft/", status=Page.DRAFT)
        self.create_page("/other-site/", site=self.other_site)

        pages = Page.objects.accessible_by(self.user, site=self.site)

        self.assertEqual(set(pages), {public, selected})

    def test_search_queryset_uses_the_same_access_policy(self):
        public = self.create_page("/public/")
        selected = self.create_page("/selected/", registration_required=True)
        selected.users.add(self.user)
        self.create_page("/hidden/", registration_required=True).users.add(
            self.other_user
        )
        request = self.request_factory.get("/search/")
        request.user = self.user

        pages = Page.get_search_queryset(request)

        self.assertEqual(set(pages), {public, selected})

    def test_sitemap_contains_only_public_pages_for_current_site(self):
        public = self.create_page("/public/")
        self.create_page("/members/", registration_required=True)
        self.create_page("/draft/", status=Page.DRAFT)
        self.create_page("/other-site/", site=self.other_site)

        pages = PageSitemap().items()

        self.assertEqual(list(pages), [public])

    def test_get_pages_template_tag_uses_the_same_access_policy(self):
        public = self.create_page("/public/")
        selected = self.create_page("/selected/", registration_required=True)
        selected.groups.add(Group.objects.create(name="Members"))
        self.user.groups.add(selected.groups.get())
        request = self.request_factory.get("/")
        request.user = self.user
        context = Context({"request": request, "user": self.user})
        node = PageNode("visible_pages", user="user")

        node.render(context)

        self.assertEqual(set(context["visible_pages"]), {public, selected})
