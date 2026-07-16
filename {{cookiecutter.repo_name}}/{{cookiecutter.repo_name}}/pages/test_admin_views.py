import json

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import Client, TestCase
from django.urls import reverse

from .models import Page, PageContentText


class SaveContentPositionTests(TestCase):
    csrf_token = "a" * 32

    def setUp(self):
        site = Site.objects.get_current()
        self.page = self.create_page("/page/")
        self.page.sites.add(site)
        self.other_page = self.create_page("/other/")
        self.other_page.sites.add(site)
        content_type = ContentType.objects.get_for_model(PageContentText)
        self.first = PageContentText.objects.create(
            page=self.page,
            content_type=content_type,
            name="First",
            position=0,
        )
        self.second = PageContentText.objects.create(
            page=self.page,
            content_type=content_type,
            name="Second",
            position=1,
        )
        self.other = PageContentText.objects.create(
            page=self.other_page,
            content_type=content_type,
            name="Other",
            position=0,
        )
        self.user = get_user_model().objects.create_superuser(
            username="admin",
            password="password",
            email="admin@example.com",
        )
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.user)

    def create_page(self, url):
        return Page.objects.create(
            url=url,
            title=url.strip("/").title(),
            status=Page.PUBLISHED,
        )

    def save_url(self, page=None):
        return reverse(
            "admin:pages_page_save_position",
            args=[(page or self.page).pk],
        )

    def post_order(self, order, *, include_csrf=True, page=None):
        headers = {}
        if include_csrf:
            self.client.cookies["csrftoken"] = self.csrf_token
            headers["HTTP_X_CSRFTOKEN"] = self.csrf_token
        return self.client.post(
            self.save_url(page),
            data=json.dumps({"order": order}),
            content_type="application/json",
            **headers,
        )

    def test_request_without_csrf_token_is_rejected(self):
        response = self.post_order([], include_csrf=False)

        self.assertEqual(response.status_code, 403)

    def test_valid_request_saves_normalized_order(self):
        response = self.post_order(
            [
                {"id": str(self.second.pk), "position": 99},
                {"id": str(self.first.pk), "position": -10},
            ]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"saved": True})
        self.first.refresh_from_db()
        self.second.refresh_from_db()
        self.assertEqual(self.second.position, 0)
        self.assertEqual(self.first.position, 1)

    def test_content_blocks_from_another_page_are_rejected(self):
        response = self.post_order([{"id": self.other.pk}])

        self.assertEqual(response.status_code, 400)
        self.assertIn("does not belong", response.json()["error"])

    def test_duplicate_and_malformed_ids_are_rejected(self):
        invalid_orders = (
            [{"id": self.first.pk}, {"id": self.first.pk}],
            [{"id": "not-an-id"}],
            [None],
        )

        for order in invalid_orders:
            with self.subTest(order=order):
                response = self.post_order(order)
                self.assertEqual(response.status_code, 400)

    def test_endpoint_accepts_post_only(self):
        response = self.client.get(self.save_url())

        self.assertEqual(response.status_code, 405)
