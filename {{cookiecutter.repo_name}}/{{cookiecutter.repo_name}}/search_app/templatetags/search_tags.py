from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('search_app/search_widget.html')
def search_widget():
    """
    Renders the search bar widget.
    This tag can be used in any template to display the search form.
    It returns the URL to which the form should submit.
    """
    search_url = reverse('search_app:search')
    return {'search_url': search_url}
