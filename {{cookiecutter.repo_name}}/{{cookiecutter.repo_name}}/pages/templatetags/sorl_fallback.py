"""Drop-in replacement for sorl-thumbnail's ``thumbnail`` block tag.

This module is loaded (instead of ``sorl_thumbnail``) when the project is
generated with ``use_sorl_thumbnail=n``. In that configuration no thumbnailing
backend is installed, so this shim keeps the templates working by exposing the
original image/file under the ``as`` alias and rendering the block body
unchanged. Geometry and cropping options are accepted for signature
compatibility and then ignored.
"""

from django import template

register = template.Library()


class ThumbnailFallbackNode(template.Node):
    def __init__(self, source, as_var, nodelist):
        self.source = source
        self.as_var = as_var
        self.nodelist = nodelist

    def render(self, context):
        if self.as_var:
            try:
                value = self.source.resolve(context)
            except template.VariableDoesNotExist:
                value = None
            context[self.as_var] = value
        return self.nodelist.render(context)


@register.tag
def thumbnail(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise template.TemplateSyntaxError(
            "'thumbnail' requires at least a source and a geometry"
        )

    as_var = None
    if len(bits) >= 4 and bits[-2] == "as":
        as_var = bits[-1]

    source = parser.compile_filter(bits[1])

    nodelist = parser.parse(("empty", "endthumbnail"))
    end = parser.next_token()
    if end.contents == "empty":
        # With no backend the source is always used; drop the empty branch.
        parser.parse(("endthumbnail",))
        parser.next_token()

    return ThumbnailFallbackNode(source, as_var, nodelist)
