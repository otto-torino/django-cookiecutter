from constance.apps import ConstanceConfig
from django.utils.translation import gettext_lazy as _


class SettingsConfig(ConstanceConfig):
    verbose_name = _("Settings")
