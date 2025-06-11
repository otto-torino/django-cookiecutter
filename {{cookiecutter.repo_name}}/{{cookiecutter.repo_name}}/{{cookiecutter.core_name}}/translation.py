from modeltranslation.translator import register, TranslationOptions
from lineup.models import MenuItem
from .models import Preferences


@register(MenuItem)
class MenuItemTranslationOptions(TranslationOptions):
    fields = (
        "label",
        "title",
    )


@register(Preferences)
class PreferencesTranslationOptions(TranslationOptions):
    fields = (
        "site_title",
        "meta_title",
        "meta_description",
        "meta_keywords",
    )
