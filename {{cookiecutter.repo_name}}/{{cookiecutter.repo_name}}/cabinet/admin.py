from django.utils.safestring import mark_safe
from cabinet.base_admin import FileAdminBase
from cabinet.ckeditor import CKEditorFilebrowserMixin
from cabinet.models import File
from django.contrib import admin
from django.template.defaultfilters import filesizeformat
from django.utils.formats import date_format
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _
from sorl.thumbnail import get_thumbnail


@admin.register(File)
class FileAdmin(CKEditorFilebrowserMixin, FileAdminBase):
    list_display = ["admin_thumbnail", "admin_file_name", "admin_details", "admin_url"]
    list_display_links = ["admin_thumbnail", "admin_file_name"]

    @admin.display(description="")
    def admin_thumbnail(self, instance):
        if instance.image_file.name:
            try:
                target = get_thumbnail(instance.image_file, "30x30", crop="center")
                return format_html(
                    '<img src="{}" alt=""/>', target.url, instance.image_alt_text
                )
            except Exception:
                return mark_safe('<span class="fa fa-file-circle-exclamation"></span>')
        elif instance.download_file.name:
            return format_html(
                '<i class="fa fa-file-{}"></i>',
                instance.download_type,
            )
        return ""

    @admin.display(description=_("file name"))
    def admin_file_name(self, instance):
        return format_html(
            "{} <small>({})</small>",
            instance.file_name,
            filesizeformat(instance.file_size),
        )

    @admin.display(description=_("details"))
    def admin_details(self, instance):
        details = [
            instance.caption,
            instance.copyright,
            _("Created %(created_at)s, last modified %(updated_at)s")
            % {
                "created_at": date_format(instance.created_at, "SHORT_DATE_FORMAT"),
                "updated_at": date_format(instance.updated_at, "SHORT_DATE_FORMAT"),
            },
        ]
        return format_html(
            "<small>{}</small>",
            format_html_join(mark_safe("<br>"), "{}", ((d,) for d in details if d)),
        )

    @admin.display(description=_("URL"))
    def admin_url(self, instance):
        if instance.image_file.name:
            return mark_safe(
                '{} <a href="javascript:void(0)" onclick="navigator.clipboard.writeText(\'{}\')"> <i class="fa fa-clipboard d-inline-block ms-2"></a>'.format(
                    instance.image_file.url, instance.image_file.url
                )
            )
        elif instance.download_file.name:
            return mark_safe(
                '{} <a href="javascript:void(0)" onclick="navigator.clipboard.writeText(\'{}\')"> <i class="fa fa-clipboard d-inline-block ms-2"></a>'.format(
                    instance.download_file.url, instance.download_file.url
                )
            )
        return ""


# Register attachment content block to admin if pages app is installed
try:
    from pages.admin import PageContentAdmin

    from .models import PageContentMultiAttachment, AttachmentModel

    class EventFileInline(admin.TabularInline):
        """
        Tabular Inline View for EventFile
        """
        model = AttachmentModel
        extra = 1
        raw_id_fields = ("file",)
        classes = (
            "collapse-entry",
            "expand-first",
        )
        fields = ["file", "position", "name", "description"] 

    @admin.register(PageContentMultiAttachment)
    class PageContentMultiAttachmentAdmin(PageContentAdmin):
        """Admin View for PageContentMultiAttachment"""

        list_display = ("id",)
        inlines = [EventFileInline]
        fieldsets = (
            (
                _("Main"),
                {
                    "fields": (
                        "name",
                    ),
                    "classes": (
                        "baton-tabs-init",
                        "baton-tab-inline-files",
                        "baton-tab-fs-adv"
                    ),
                },
            ),
            (
                _("Advanced options"),
                {
                    "classes": ("tab-fs-adv",),
                    "fields": (
                        "enabled",
                        "use_accordion",
                        "show_name",
                        "background_color",
                    ),
                },
            ),
        )

except ImportError:
    pass
