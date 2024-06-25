from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from preferences_utils.models import PreferencesUtilsModel


# custom user model just in case we need to add functionality
class User(AbstractUser):
    pass

{% if cookiecutter.admin == 'django-baton' %}
def ai_models_default():
    return {
    "TRANSLATIONS": "gpt-4o",
    "SUMMARIZATIONS": "gpt-3.5-turbo",
    "CORRECTIONS": "gpt-3.5-turbo",
    "IMAGES": "dall-e-3"
}
{% endif %}

@PreferencesUtilsModel.register("pref")
class Preferences(PreferencesUtilsModel):
    {% if cookiecutter.admin == 'django-baton' %}ai_models = models.JSONField(_("ai models"), default=ai_models_default){% endif %}
    hide_archived = models.BooleanField(verbose_name=_("nascondi archiviati"),default=False)
    robots = models.TextField(_("robots"), default="", blank=True)

    site_title = models.CharField(_('titolo sito'), max_length=100, default="{{ cookiecutter.project_name }}", blank=True)

    meta_title = models.CharField(_('titolo meta'), max_length=100, default="{{ cookiecutter.project_name }}", blank=True)
    meta_description = models.CharField(_('descrizione meta'), max_length=300, default="{{ cookiecutter.project_description }}", blank=True)
    meta_image = models.ImageField(_('immagine meta'), upload_to='preferences/', blank=True, null=True)
    meta_keywords = models.CharField(_('parole chiave meta'), max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _("preferenze")
        verbose_name_plural = _("preferenze")
