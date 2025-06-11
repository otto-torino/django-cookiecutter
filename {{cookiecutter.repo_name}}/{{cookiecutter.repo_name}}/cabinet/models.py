from cabinet.base import (
    AbstractFile,
    DownloadMixin,
    ImageMixin,
    OverwriteMixin,
    TimestampsMixin,
)
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.db.models import Q, signals
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from tree_queries.models import TreeNode
from pages.models import AccordionBlock

if not hasattr(settings, "CABINET_FILE_MODEL"):  # pragma: no branch
    settings.CABINET_FILE_MODEL = "cabinet.File"


def get_file_model():
    """
    Return the File model that is active in this project.
    """
    try:
        return apps.get_model(settings.CABINET_FILE_MODEL, require_ready=False)
    except ValueError as exc:
        raise ImproperlyConfigured(
            "CABINET_FILE_MODEL must be of the form 'app_label.model_name'"
        ) from exc
    except LookupError as exc:
        raise ImproperlyConfigured(
            "CABINET_FILE_MODEL refers to model '%s'"
            " that has not been installed" % settings.CABINET_FILE_MODEL
        ) from exc


class Folder(TimestampsMixin, TreeNode):
    name = models.CharField(_("name"), max_length=100)

    class Meta:  # pyright: ignore
        ordering = ["name"]
        unique_together = [("parent", "name")]
        verbose_name = _("folder")
        verbose_name_plural = _("folders")

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if (
            not self.parent_id  # pyright: ignore
            and Folder.objects.filter(~Q(pk=self.pk), Q(name=self.name)).exists()
        ):
            raise ValidationError(
                {"name": _("Root folder with same name exists already.")}
            )

    def ancestors_including_self(self):
        return self.ancestors(include_self=True)


class File(AbstractFile, ImageMixin, DownloadMixin, OverwriteMixin):  # pyright: ignore
    FILE_FIELDS = ["image_file", "download_file"]

    caption = models.CharField(_("caption"), max_length=1000, blank=True)
    copyright = models.CharField(_("copyright"), max_length=1000, blank=True)

    class Meta(AbstractFile.Meta):  # pyright: ignore
        swappable = "CABINET_FILE_MODEL"


# Register Attachment content block if pages app is installed
try:
    from cabinet.fields import CabinetForeignKey
    from pages.models import PageContent

    class PageContentMultiAttachment(PageContent, AccordionBlock):
        def __str__(self):
            return f"{self.page.title}/{_('attachment content')}"

        class Meta:  # pyright: ignore
            verbose_name = _("attachment content block")
            verbose_name_plural = _("attachment content blocks")

        def class_name(self):
            return self.__class__.__name__

        @property
        def get_unique_id(self):
            return "Attachment" + str(self.pk)

        def get_content_label(self):
            return _("Attachment")

        def get_content_description(self):
            return _("Attachment content")

        def get_add_form_url(self):
            return reverse_lazy("admin:cabinet_pagecontentmultiattachment_add")

        def get_change_form_url(self):
            return reverse_lazy(
                "admin:cabinet_pagecontentmultiattachment_change", args=[self.pk]
            )

        def get_delete_url(self):
            return reverse_lazy(
                "admin:cabinet_pagecontentmultiattachment_delete", args=[self.pk]
            )

        def get_preview_template(self):
            return "admin/cabinet/page_content_multi_attachment/preview.html"

        def get_render_template(self):
            return "cabinet/page_content_multi_attachment.html"

    class AttachmentModel(models.Model):
        file = CabinetForeignKey(
            File,
            on_delete=models.RESTRICT,
            verbose_name=_("file"),
            blank=True,
            null=True,
        )
        description = models.TextField(_("descrizione"), blank=True, null=True)

        position = models.IntegerField(_("ordinamento"), default=0)
        name = models.CharField(_("nome"), max_length=200)
        page_content = models.ForeignKey(
            PageContentMultiAttachment,
            related_name="files",
            on_delete=models.CASCADE,
            verbose_name=_("contenuto"),
        )

        class Meta:  # pyright: ignore
            verbose_name = _("file")
            verbose_name_plural = _("file")
            ordering = ("position",)

        def __str__(self):
            return str(self.file)

except ImportError:
    pass


@receiver(signals.post_delete, sender=File)
def delete_files(sender, instance, **kwargs):
    instance.delete_files()
