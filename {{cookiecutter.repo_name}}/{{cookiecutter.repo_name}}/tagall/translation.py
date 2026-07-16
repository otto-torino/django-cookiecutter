from modeltranslation.translator import TranslationOptions, register

from .models import Tag


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ("name",)
