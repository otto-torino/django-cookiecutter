from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from .models import Searchable


class SearchableTests(SimpleTestCase):
    def test_search_queryset_must_be_defined_explicitly(self):
        with self.assertRaisesMessage(
            ImproperlyConfigured,
            "Searchable must define a get_search_queryset(request) method.",
        ):
            Searchable.get_search_queryset(request=None)
