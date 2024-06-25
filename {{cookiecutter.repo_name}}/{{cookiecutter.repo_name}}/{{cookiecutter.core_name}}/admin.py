from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from preferences_utils.admin import PreferencesUtilsAdmin

from .models import User, Preferences


class ArchivedModelAdmin(admin.ModelAdmin):
    """ Utility class to filter out archived records """
    def get_queryset(self, request):
        pref = Preferences.instance()
        qs = super().get_queryset(request)
        if pref.hide_archived:
             qs = qs.exclude(status=self.model.ARCHIVED)
        return qs


# register the user admin
admin.site.register(User, UserAdmin)


@admin.register(Preferences)
class PreferencesAdmin(PreferencesUtilsAdmin):
    list_display = ('id', )

    fieldsets = (
        (_('Principale'), {
            {% if cookiecutter.admin == 'django-baton' %}'fields': ("site_title", "ai_models", "hide_archived", "robots",),{% endif %}
            {% if cookiecutter.admin != 'django-baton' %}'fields': ("site_title", "hide_archived", "robots",),{% endif %}
            "classes": ("baton-tabs-init", "baton-tab-fs-meta", ),
        }),
        (_('Meta'), {
            'fields': ("meta_title", "meta_description", "meta_image", "meta_keywords",),
            "classes": ("tab-fs-meta",),
        }),
    )
