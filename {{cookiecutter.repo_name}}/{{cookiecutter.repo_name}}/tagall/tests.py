import json

from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import resolve, reverse

from pages.models import Page

from .models import Tag
from .views import TagallCreateTagsView


class TagTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_save_generates_unique_slugs(self):
        first = Tag.objects.create(name="Medioevo")
        second = Tag.objects.create(name="Medioevo!")

        self.assertEqual(first.slug, "medioevo")
        self.assertEqual(second.slug, "medioevo-2")

    def test_save_includes_generated_slug_with_update_fields(self):
        tag = Tag.objects.create(name="Medioevo")
        Tag.objects.filter(pk=tag.pk).update(slug="")
        tag.refresh_from_db()

        tag.save(update_fields=["name"])

        tag.refresh_from_db()
        self.assertEqual(tag.slug, "medioevo")

    def test_baton_create_tags_url_uses_local_view(self):
        url = {% if cookiecutter.use_translations == 'y' %}"/{{ cookiecutter.default_language }}/baton/create-tags/"{% else %}"/baton/create-tags/"{% endif %}

        match = resolve(url)

        self.assertIs(match.func.view_class, TagallCreateTagsView)

    def test_baton_create_tags_creates_tag(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )
        request = self.request_factory.post(
            "/baton/create-tags/",
            data=json.dumps(
                {
                    "appLabel": "pages",
                    "modelName": "page",
                    "field": "tags",
                    "labels": ["Medioevo"],
                }
            ),
            content_type="application/json",
        )
        request.user = user

        response = TagallCreateTagsView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        tag = Tag.objects.get(name="Medioevo")
        self.assertEqual(tag.slug, "medioevo")
        {% if cookiecutter.use_translations == 'y' %}self.assertEqual(tag.name_{{ cookiecutter.default_language }}, "Medioevo"){% endif %}

    def test_page_admin_configures_baton_tag_suggestions(self):
        page_admin = admin.site._registry[Page]

        self.assertEqual(
            page_admin.baton_tag_suggestion_fields["tags"]["label_field"],
            "name",
        )

    def test_admin_used_by_shows_related_objects(self):
        tag = Tag.objects.create(name="Medioevo")
        page = Page.objects.create(url="/medioevo/", title="Medioevo")
        page.tags.add(tag)

        tag_admin = admin.site._registry[Tag]
        html = str(tag_admin.used_by(tag))

        self.assertIn(reverse("admin:pages_page_change", args=(page.pk,)), html)

    def test_admin_merge_moves_relations_and_deletes_source_tags(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )
        target = Tag.objects.create(name="History")
        source = Tag.objects.create(name="Medioevo")
        page = Page.objects.create(url="/medioevo/", title="Medioevo")
        page.tags.add(source)
        self.client.force_login(user)

        response = self.client.post(
            reverse("admin:tagall_tag_changelist"),
            {
                "action": "merge_tags",
                "apply": "1",
                "tags": [str(target.pk), str(source.pk)],
                "target_tag": str(target.pk),
                helpers.ACTION_CHECKBOX_NAME: [str(target.pk), str(source.pk)],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tag.objects.filter(pk=source.pk).exists())
        self.assertEqual(list(page.tags.all()), [target])
