from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from preferences_utils.admin import PreferencesUtilsAdmin
{% if cookiecutter.use_translations == 'y' %}from modeltranslation.admin import TranslationAdmin, TranslationStackedInline
from lineup.models import MenuItem
from lineup.admin import MenuItemAdmin as BaseMenuItemAdmin{% endif %}

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
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', )
    fieldsets = (
        ('Main', {
            'fields': ('username', 'password', ),
            'classes': ('baton-tabs-init', 'baton-tab-fs-info', 'baton-tab-fs-permissions', 'baton-tab-fs-dates', ),

        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', ),
            'classes': ('tab-fs-info', ),

        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', ),
            'classes': ('tab-fs-permissions', ),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', ),
            'classes': ('tab-fs-dates', ),
        }),
    )

admin.site.register(User, CustomUserAdmin)


@admin.register(Preferences)
class PreferencesAdmin(PreferencesUtilsAdmin):
    list_display = ('id', )

    fieldsets = (
        (_('Principale'), {
            'fields': ("site_title", "ai_models", "hide_archived", "robots",),
            "classes": ("baton-tabs-init", "baton-tab-fs-meta", ),
        }),
        (_('Meta'), {
            'fields': ("meta_title", "meta_description", "meta_image", "meta_keywords",),
            "classes": ("tab-fs-meta",),
        }),
    )

{% if cookiecutter.use_translations == 'y' %}
# Custom menu admin
class MenuItemInline(TranslationStackedInline):
    """
    Tabular Inline View for MenuItem
    """

    model = MenuItem
    extra = 1
    classes = (
        "collapse-entry",
        "expand-first",
    )
    prepopulated_fields = {"slug": ("label",)}

admin.site.unregister(MenuItem)


@admin.register(MenuItem)
class MenuItemAdmin(TranslationAdmin, BaseMenuItemAdmin): # type: ignore
    inlines = [
        MenuItemInline,
    ]
{% endif %}
