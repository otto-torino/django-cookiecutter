from django.db import models
from django.core.exceptions import ImproperlyConfigured

class Searchable(models.Model):
    """
    An abstract model that provides an interface for full-text searching.

    Any model in another app that should be included in the site-wide search
    results must inherit from this class.

    Attributes:
        search_fields (list): A list of field names (as strings) on the inheriting
                              model that should be included in the search index.
                              This MUST be overridden by the child model.

    Methods:
        get_absolute_url(): Returns the canonical URL for an instance of the model.
                            This MUST be overridden by the child model to provide
                            a link to the object in the search results.
        get_search_queryset(request): Returns only the objects discoverable by
                                      the current request. This MUST be overridden
                                      by the child model.
    """
    search_fields = []

    class Meta:
        abstract = True

    def get_absolute_url(self):
        """
        Returns the absolute URL for the instance.
        This method must be implemented by the concrete model.
        """
        raise ImproperlyConfigured(
            f"{self.__class__.__name__} is missing a get_absolute_url() method."
        )

    @classmethod
    def get_search_fields(cls):
        """
        A class method to get the defined search fields.
        """
        if not cls.search_fields or not isinstance(cls.search_fields, list):
            raise ImproperlyConfigured(
                f"{cls.__name__} must define a 'search_fields' list."
            )
        return cls.search_fields

    @classmethod
    def get_search_queryset(cls, request):
        """Return objects the current request is allowed to discover."""
        raise ImproperlyConfigured(
            f"{cls.__name__} must define a get_search_queryset(request) method."
        )
