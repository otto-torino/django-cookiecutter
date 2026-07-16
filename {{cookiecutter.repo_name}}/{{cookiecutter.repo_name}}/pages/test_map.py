from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.test import TestCase

from .forms import PageContentMapItemAdminForm
from .models import Page, PageContentMap, PageContentMapItem


class MapContentTests(TestCase):
    def setUp(self):
        site = Site.objects.get_current()
        self.page = Page.objects.create(
            url="/map/",
            title="Map",
            status=Page.PUBLISHED,
        )
        self.page.sites.add(site)
        self.block = PageContentMap.objects.create(
            page=self.page,
            content_type=ContentType.objects.get_for_model(PageContentMap),
            name="Map",
            position=0,
        )

    def map_item(self, **kwargs):
        values = {
            "block": self.block,
            "shape": PageContentMapItem.Shape.POINT,
            "coordinates": [45.0, 7.0],
            "name": "Point",
        }
        values.update(kwargs)
        return PageContentMapItem(**values)

    def test_supported_shapes_accept_structured_coordinates(self):
        valid_coordinates = {
            PageContentMapItem.Shape.POINT: [45.0, 7.0],
            PageContentMapItem.Shape.POLYLINE: [[45.0, 7.0], [46.0, 8.0]],
            PageContentMapItem.Shape.POLYGON: [
                [45.0, 7.0],
                [46.0, 8.0],
                [44.0, 8.0],
            ],
            PageContentMapItem.Shape.CIRCLE: {
                "lat": 45.0,
                "lng": 7.0,
                "radius": 500,
            },
        }

        for shape, coordinates in valid_coordinates.items():
            with self.subTest(shape=shape):
                self.map_item(shape=shape, coordinates=coordinates).full_clean()

    def test_coordinates_reject_code_and_invalid_geography(self):
        invalid_coordinates = (
            "[45, 7]; alert('xss')",
            [91, 7],
            [45, 181],
            [45],
        )

        for coordinates in invalid_coordinates:
            with self.subTest(coordinates=coordinates):
                with self.assertRaises(ValidationError):
                    self.map_item(coordinates=coordinates).full_clean()

    def test_admin_form_converts_widget_json_to_structured_coordinates(self):
        form = PageContentMapItemAdminForm(
            data={
                "block": self.block.pk,
                "shape": PageContentMapItem.Shape.POINT,
                "coordinates": "[45.0, 7.0]",
                "name": "Point",
                "color": "#000000",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["coordinates"], [45.0, 7.0])

    def test_map_links_allow_only_relative_or_http_urls(self):
        self.map_item(link="/contacts/").full_clean()
        self.map_item(link="https://example.com/place").full_clean()

        for link in ("javascript:alert(1)", "data:text/html,danger", "//evil.test"):
            with self.subTest(link=link), self.assertRaises(ValidationError):
                self.map_item(link=link).full_clean()

    def test_map_payload_fails_closed_for_invalid_legacy_values(self):
        item = self.map_item(
            coordinates="alert('xss')",
            link="javascript:alert(1)",
            color="not-a-color",
        )

        payload = item.as_map_data()

        self.assertIsNone(payload["coordinates"])
        self.assertEqual(payload["link"], "")
        self.assertEqual(payload["color"], "#000000")

    def test_template_serializes_untrusted_text_without_executing_it(self):
        attack = "</script><script>alert('xss')</script>"
        PageContentMapItem.objects.create(
            block=self.block,
            shape=PageContentMapItem.Shape.POINT,
            coordinates=[45.0, 7.0],
            name=attack,
            caption=attack,
            link="javascript:alert(1)",
        )

        rendered = render_to_string(
            "pages/includes/map_script.html",
            {"map_object": self.block},
        )

        self.assertNotIn(attack, rendered)
        self.assertNotIn("javascript:alert(1)", rendered)
        self.assertIn(r"\u003C/script\u003E", rendered)
        self.assertIn("caption.textContent = item.caption", rendered)
