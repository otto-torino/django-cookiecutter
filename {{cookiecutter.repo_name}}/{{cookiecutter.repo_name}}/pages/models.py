from __future__ import unicode_literals

import logging

from ckeditor_uploader.fields import RichTextUploadingField
from colorfield.fields import ColorField
from baton.fields import BatonAiImageField
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.sites.models import Site
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import get_script_prefix, reverse_lazy
from django.utils import timezone
from django.utils.encoding import iri_to_uri
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django_extensions.db.models import TimeStampedModel
from taggit.managers import ContentType
from taggit_autosuggest.managers import TaggableManager
from .managers import PageContentQuerySet, PageManager
from search_app.models import Searchable

User = get_user_model()
logger = logging.getLogger(__name__)

class AccordionBlock(models.Model):
    use_accordion = models.BooleanField(
        default=False,
        help_text=_(
            "set to true if you want this block to be inside an accordion, the block name will be used inside the accordion head"
        ),
    )

    class Meta:  # pyright: ignore
        abstract = True
        verbose_name = _("accordion")
        verbose_name_plural = _("accordions")


class Page(TimeStampedModel, Searchable):
    DRAFT = 1
    PUBLISHED = 2
    ARCHIVED = 3

    STATUS_CHOICES = (
        (DRAFT, _("bozza")),
        (PUBLISHED, _("pubblicato")),
        (ARCHIVED, _("archiviato")),
    )

    HIGH_RELEVANCE = 1
    MEDIUM_RELEVANCE = 2
    LOW_RELEVANCE = 3

    RELEVANCE_CHOICES = (
        (HIGH_RELEVANCE, _("alta")),
        (MEDIUM_RELEVANCE, _("media")),
        (LOW_RELEVANCE, _("bassa")),
    )

    parent = models.ForeignKey(
        "self",
        verbose_name=_("parent"),
        on_delete=models.SET_NULL,
        related_name="children",
        blank=True,
        null=True,
        help_text=_("Used to compose breadcrumbs"),
    )
    url = models.CharField(_("URL"), max_length=100, db_index=True)
    title = models.CharField(_("title"), max_length=200)
    image = BatonAiImageField(
        verbose_name=_("immagine header"),
        upload_to="pages/images/",
        subject_location_field="subject_location",
        alt_field={% if cookiecutter.use_translations == 'y' %}"alt_text_{{ cookiecutter.default_language }}"{% else %}"alt_text"{% endif %},
        blank=True,
        null=True,
    )
    alt_text = models.CharField(_("alt text"), max_length=200, blank=True)
    subject_location = models.CharField(max_length=7, default="50,50")
    tags = TaggableManager(_("tags"), blank=True)
    template_name = models.CharField(
        _("template name"),
        max_length=70,
        blank=True,
        help_text=_(
            "Example: 'pages/contact_page.html'. If this isn't provided, "
            "the system will use 'pages/default.html'."
        ),
    )
    registration_required = models.BooleanField(
        _("registration required"),
        help_text=_(
            "If this is checked, only logged-in users will be able to view the page."
        ),  # noqa
        default=False,
    )
    users = models.ManyToManyField(
        User,
        verbose_name=_("users"),
        related_name="pages",
        blank=True,
        help_text=_(
            "If registration is required and users are filled, than only this users can access the content."
        ),
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        related_name="pages",
        help_text=_(
            "If registration is required and groups are filled, than only users belonging to these groups can access the content."
            # noqa: E501
        ),
    )
    enable_social_sharing = models.BooleanField(
        _("enable social sharing"), default=False
    )
    last_updated = models.BooleanField(
        _("last updated"), default=True, help_text=_("show last updated date")
    )
    sites = models.ManyToManyField(Site, verbose_name=_("sites"))
    status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT)
    relevance = models.IntegerField(
        verbose_name=_("rilevanza"),
        help_text=_("priority level for searches"),
        choices=RELEVANCE_CHOICES,
        default=2,
    )

    # seo
    meta_title = models.CharField(
        _("meta title"),
        max_length=200,
        blank=True,
        null=True,
        help_text=_("default to page title"),
    )
    meta_description = models.TextField(
        _("meta description"),
        blank=True,
        null=True,
        help_text=_("default to first 20 words of content"),
    )
    meta_keywords = models.CharField(
        _("meta keywords"),
        max_length=200,
        blank=True,
        null=True,
        help_text=_("default to page tags"),
    )

    search_fields = [
        # Page fields
        'title',
        'meta_title',
        'meta_description',
        'meta_keywords',

        # PageContent fields
        'content_blocks__pagecontenttext__content',
        'content_blocks__pagecontentimage__caption',
        'content_blocks__pagecontentimage__credits',
        'content_blocks__pagecontenttextimage__text',
        'content_blocks__pagecontenttextimage__caption',
        'content_blocks__pagecontenttextimage__credits',
        'content_blocks__pagecontentmultiimage__images__caption',
        'content_blocks__pagecontentmultiimage__images__credits',
        'content_blocks__pagecontentboxmenu__images__name',
        'content_blocks__pagecontentmap__text',
        'content_blocks__pagecontentmap__items__name',
        'content_blocks__pagecontentmap__items__caption',
        'content_blocks__pagecontentvideo__description',
        'content_blocks__pagecontentvideo__credits',
        'content_blocks__pagecontentlayout__layout_items__text',
    ]

    objects: PageManager = PageManager()  # pyright: ignore

    class Meta:  # pyright: ignore
        verbose_name = _("page")
        verbose_name_plural = _("pages")
        ordering = ("url",)

    def __str__(self):
        return "%s -- %s" % (self.url, self.title)

    def get_absolute_url(self):
        # Handle script prefix manually because we bypass reverse()
        return iri_to_uri(
            get_script_prefix().rstrip("/") + f"/p{self.url}"
        )

    def has_map_content(self):
        for c in self.content_blocks.filter(enabled=True, layout_content=False):  # pyright: ignore
            if c.content_type.model == "pagecontentmap":
                return True
        return False

    @property
    def breadcrumbs(self):
        p = self
        res = []
        while p.parent is not None:
            res.insert(
                0,
                {
                    "url": p.parent.get_absolute_url(),
                    "label": p.parent.title,
                },
            )
            p = p.parent
        return res


class PageContent(TimeStampedModel):
    """This is a base class model which page content providers should extend"""

    COLOR_PALETTE = [
        ("#D0E8F3", _("blue")),
        ("#AADAC5", _("green")),
        ("#F0E8DB", _("beige")),
        ("#DCD5C8", _("brown")),
    ]

    layout_content = models.BooleanField(
        _("layout content"),
        default=False,
        help_text=_("if true this content can only be used inside a layout block, in that case probably you also want it to have full width"),
    )
    name = models.CharField(_("name"), max_length=200)
    show_name = models.BooleanField(_("show name"), default=False)
    background_color = ColorField(
        _("background color"), samples=COLOR_PALETTE, blank=True, null=True
    )
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        editable=False,
        related_name="content_blocks",
    )
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, editable=False
    )
    object_id = models.PositiveIntegerField(blank=True, null=True, editable=False)
    content_object = GenericForeignKey("content_type", "object_id")
    position = models.IntegerField(_("ordering"), editable=False)
    enabled = models.BooleanField(_("block enabled"), default=True)
    full_width = models.BooleanField(
        _("full width"),
        default=False,
        help_text=_("set to true if you want the block to fill the page width"),
    )

    objects = PageContentQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if self and self.page:
            self.page.modified = timezone.now()
            self.page.save()
        super(PageContent, self).save(*args, **kwargs)

    def class_name(self):
        raise NotImplementedError

    def get_content_label(self):
        raise NotImplementedError

    def get_content_description(self):
        raise NotImplementedError

    def get_add_form_url(self):
        raise NotImplementedError

    def get_change_form_url(self):
        raise NotImplementedError

    def get_preview_template(self):
        raise NotImplementedError

    def get_render_template(self):
        raise NotImplementedError

    @property
    def get_unique_id(self):
        raise NotImplementedError

    def __str__(self):
        return f"{self.name}"

    class Meta:  # pyright: ignore
        ordering = ["position"]


class PageContentText(PageContent, AccordionBlock):
    content = RichTextUploadingField(verbose_name=_("content"), blank=True)
    url = models.CharField(_("url"), blank=True, null=True)
    text_color = ColorField(
        _("text color"),
        help_text=_("set the text color, leave empty to use inherited default color"),
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.page.title}/{_('text content')}"

    class Meta:  # pyright: ignore
        verbose_name = _("text content block")
        verbose_name_plural = _("text content blocks")

    def class_name(self):
        return self.__class__.__name__

    def get_content_label(self):
        return _("Text")

    def get_content_description(self):
        return _("Pure text content from editor")

    def get_add_form_url(self):
        url = reverse_lazy("admin:pages_pagecontenttext_add")
        logger.info(url)
        return reverse_lazy("admin:pages_pagecontenttext_add")

    def get_change_form_url(self):
        return reverse_lazy("admin:pages_pagecontenttext_change", args=[self.pk])

    def get_delete_url(self):
        return reverse_lazy("admin:pages_pagecontenttext_delete", args=[self.pk])

    def get_preview_template(self):
        return "admin/pages/page_content_text/preview.html"

    def get_render_template(self):
        return "pages/page_content_text.html"

    @property
    def get_unique_id(self):
        return "Text" + str(self.pk)


class PageContentImage(PageContent):
    image = BatonAiImageField(
        verbose_name=_("image"),
        upload_to="pages/image_content/",
        subject_location_field="subject_location",
        alt_field={% if cookiecutter.use_translations == 'y' %}"caption_{{ cookiecutter.default_language }}"{% else %}"caption"{% endif %},
    )
    subject_location = models.CharField(max_length=7, default="50,50")
    caption = models.TextField(_("caption"), blank=True, null=True)
    show_captions = models.BooleanField(
        _("show captions"),
        default=True,
        help_text=_("set to true if you want to show the captions of the images"),
    )
    credits = models.TextField(_("credits"), blank=True, null=True)
    url = models.CharField(_("url"), blank=True, null=True)

    def __str__(self):
        return f"{self.page.title}/{_('image content')}"

    class Meta:  # pyright: ignore
        verbose_name = _("image content block")
        verbose_name_plural = _("image content blocks")

    def class_name(self):
        return self.__class__.__name__

    def get_content_label(self):
        return _("Image")

    def get_content_description(self):
        return _("Full width image")

    def get_add_form_url(self):
        return reverse_lazy("admin:pages_pagecontentimage_add")

    def get_change_form_url(self):
        return reverse_lazy("admin:pages_pagecontentimage_change", args=[self.pk])

    def get_delete_url(self):
        return reverse_lazy("admin:pages_pagecontentimage_delete", args=[self.pk])

    def get_preview_template(self):
        return "admin/pages/page_content_image/preview.html"

    def get_render_template(self):
        return "pages/page_content_image.html"

    @property
    def get_unique_id(self):
        return "Image" + str(self.pk)


class PageContentTextImage(PageContent, AccordionBlock):
    CHOICES = (
        ("left", _("Left")),
        ("right", _("Right")),
        ("top", _("Top")),
        ("bottom", _("Bottom")),
    )
    text = RichTextUploadingField(verbose_name=_("text"), blank=True)
    # specify the width of the left column in percentage
    left_column_width = models.IntegerField(
        _("left column width (%)"),
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True,
    )
    image = BatonAiImageField(
        verbose_name=_("image"),
        upload_to="pages/text_image_content",
        subject_location_field="subject_location",
        alt_field={% if cookiecutter.use_translations == 'y' %}"caption_{{ cookiecutter.default_language }}"{% else %}"caption"{% endif %},
    )
    subject_location = models.CharField(max_length=7, default="50,50")
    image_position = models.CharField(
        _("image position"), max_length=6, choices=CHOICES, default="right"
    )
    show_captions = models.BooleanField(
        _("show captions"),
        default=True,
        help_text=_("set to true if you want to show the captions of the images"),
    )
    caption = models.TextField(_("caption"), blank=True, null=True)
    credits = models.TextField(_("credits"), blank=True, null=True)

    def __str__(self):
        return f"{self.page.title}/{_('text and image content')}"

    class Meta:  # pyright: ignore
        verbose_name = _("text and image content block")
        verbose_name_plural = _("text and image content blocks")

    def class_name(self):
        return self.__class__.__name__

    def get_content_label(self):
        return _("Text and image")

    def get_content_description(self):
        return _("Text and image content")

    def get_add_form_url(self):
        return reverse_lazy("admin:pages_pagecontenttextimage_add")

    def get_change_form_url(self):
        return reverse_lazy("admin:pages_pagecontenttextimage_change", args=[self.pk])

    def get_delete_url(self):
        return reverse_lazy("admin:pages_pagecontenttextimage_delete", args=[self.pk])

    def get_preview_template(self):
        return "admin/pages/page_content_textimage/preview.html"

    def get_render_template(self):
        return "pages/page_content_textimage.html"

    @property
    def get_unique_id(self):
        return "TextImage" + str(self.pk)


class PageContentMultiImage(PageContent):
    CHOICES = (
        ("carousel", _("Carousel")),
        ("grid", _("Grid")),
        # ("masonry", _("Masonry")),
    )
    type = models.CharField(
        verbose_name=_("choose representation type"),
        max_length=20,
        choices=CHOICES,
        default="carousel",
    )
    show_captions = models.BooleanField(
        _("show captions"),
        default=True,
        help_text=_("set to true if you want to show the captions of the images"),
    )
    height = models.IntegerField(
        _("carousel max height"),
        default=450,
        help_text=_("set the max height of the carousel images in pixels"),
    )
    crop = models.BooleanField(
        _("crop images"),
        default=False,
        help_text=_("set to true if you want to crop the images"),
    )
    crop_size = models.CharField(
        _("crop size"),
        default="600x500",
        help_text=_("size should be wxh"),
    )
    image_list = models.JSONField(verbose_name=_("image list"), blank=True, null=True)

    def __str__(self):
        return f"{self.page.title}/{_('multi image content')}"

    class Meta:  # pyright: ignore
        verbose_name = _("multi image content block")
        verbose_name_plural = _("multi image content blocks")

    def class_name(self):
        return self.__class__.__name__

    def get_content_label(self):
        return _("Multi image")

    def get_content_description(self):
        return _("Multi image content (grid or carousel)")

    def get_add_form_url(self):
        return reverse_lazy("admin:pages_pagecontentmultiimage_add")

    def get_change_form_url(self):
        return reverse_lazy("admin:pages_pagecontentmultiimage_change", args=[self.pk])

    def get_delete_url(self):
        return reverse_lazy("admin:pages_pagecontentmultiimage_delete", args=[self.pk])

    def get_preview_template(self):
        return "admin/pages/page_content_multiimage/preview.html"

    def get_render_template(self):
        return "pages/page_content_multiimage.html"

    def get_carousel_id(self):
        return f"carousel-{self.pk}"

    @property
    def get_unique_id(self):
        return "MultiImage" + str(self.pk)


class PageContentMultiImageItem(models.Model):
    file = BatonAiImageField(
        upload_to="pages/multi_image_content",
        verbose_name=_("file"),
        subject_location_field="subject_location",
        alt_field={% if cookiecutter.use_translations == 'y' %}"caption_{{ cookiecutter.default_language }}"{% else %}"caption"{% endif %},
    )
    subject_location = models.CharField(
        _("subject coordinates"), max_length=7, default="50,50"
    )
    position = models.IntegerField(_("order"), default=0)
    caption = models.TextField(_("caption"), blank=True, null=True)
    credits = models.TextField(_("credits"), blank=True, null=True)
    block = models.ForeignKey(
        PageContentMultiImage, on_delete=models.CASCADE, related_name="images"
    )

    class Meta:  # pyright: ignore
        verbose_name = _("image")
        verbose_name_plural = _("images")
        ordering = ("position",)

    def __str__(self):
        return str(self.file)


class PageContentBoxMenu(PageContent):
    columns = models.IntegerField(
        _("columns"), help_text=_("maximum number of boxes per row"), default=5
    )
    shadow = models.BooleanField(
        _("shadow"),
        default=True,
        help_text=_(
            "set to true if you want the boxes to have a shadow on name and icon"
        ),
    )
    zoom = models.BooleanField(
        _("zoom"),
        default=False,
        help_text=_("set to true if you want the boxes to zoom on hover"),
    )
    rounding = models.IntegerField(
        _("rounding"), default=8, help_text=_("set the rounding of the boxes in pixels")
    )
    rectangular = models.BooleanField(
        _("rectangular"),
        default=False,
        help_text=_(
            "set to true if you want boxes to become rectangular when they are stretched"
        ),
    )

    def __str__(self):
        return f"{self.page.title}/{_('Box menu content')}"

    class Meta:  # pyright: ignore
        verbose_name = _("Box menu")
        verbose_name_plural = _("Box menus")

    @property
    def basis(self):
        return str(int(100 / self.columns)) + "%"

    def class_name(self):
        return self.__class__.__name__

    def get_content_label(self):
        return _("Box menu")

    def get_content_description(self):
        return _("Box menu content ")

    def get_add_form_url(self):
        return reverse_lazy("admin:pages_pagecontentboxmenu_add")

    def get_change_form_url(self):
        return reverse_lazy("admin:pages_pagecontentboxmenu_change", args=[self.pk])

    def get_delete_url(self):
        return reverse_lazy("admin:pages_pagecontentboxmenu_delete", args=[self.pk])

    def get_preview_template(self):
        return "admin/pages/page_content_boxmenu/preview.html"

    def get_render_template(self):
        return "pages/page_content_boxmenu.html"

    def get_carousel_id(self):
        return f"carousel-{self.pk}"

    @property
    def get_unique_id(self):
        return "BoxMenu" + str(self.pk)


class PageContentBoxItem(models.Model):
    file = BatonAiImageField(
        _("image"),
        upload_to="pages/box_menu_content",
        subject_location_field="subject_location",
        alt_field={% if cookiecutter.use_translations == 'y' %}"alt_text_{{ cookiecutter.default_language }}"{% else %}"alt_text"{% endif %},
        blank=True,
        null=True,
    )
    alt_text = models.CharField(_("alt text"), max_length=255, blank=True, null=True)
    subject_location = models.CharField(
        _("subject coordinates"), max_length=7, default="50,50"
    )
    name = models.CharField(verbose_name=_("name"), max_length=100, blank=True)
    link = models.CharField(
        verbose_name=_("url"),
        max_length=200,
    )
    icon = models.FileField(
        verbose_name=_("icon"),
        upload_to="pages/box_menu_items/",
        help_text="upload an svg icon",
        blank=True,
        null=True,
    )
    icon_text = models.CharField(
        verbose_name=_("testo icona"), max_length=100, blank=True, null=True
    )
    position = models.IntegerField(_("order"), default=0)
    text_color = models.CharField(
        _("text color"),
        max_length=7,
        default="#f5f5f5",
        help_text=_("set the color of box name"),
    )
    bg_color = models.CharField(
        _("background color"),
        max_length=7,
        default="#f5f5f5",
        help_text=_(
            "set the color of box background, if set will be always used instead of image on mobile devices"
        ),
    )
    block = models.ForeignKey(
        PageContentBoxMenu, on_delete=models.CASCADE, related_name="images"
    )

    def __str__(self):
        return self.name

    class Meta:  # pyright: ignore
        verbose_name = _("Box")
        verbose_name_plural = _("Boxes")
        ordering = ("position",)


class PageContentRssFeed(PageContent):
    rss_feed_url = models.URLField(_("rss feed url"), max_length=200)
    num_items = models.IntegerField(_("number of items"), default=5)

    def __str__(self):
        return f"{self.page.title}/{_('RSS feed')}"

    class Meta:  # pyright: ignore
        verbose_name = _("RSS feed block")
        verbose_name_plural = _("RSS feed blocks")

    def class_name(self):
        return self.__class__.__name__

    def get_content_label(self):
        return _("RSS feed")

    def get_content_description(self):
        return _("RSS feed articles displayed in cards")

    def get_add_form_url(self):
        return reverse_lazy("admin:pages_pagecontentrssfeed_add")

    def get_change_form_url(self):
        return reverse_lazy("admin:pages_pagecontentrssfeed_change", args=[self.pk])

    def get_delete_url(self):
        return reverse_lazy("admin:pages_pagecontentrssfeed_delete", args=[self.pk])

    def get_preview_template(self):
        return "admin/pages/page_content_rss_feed/preview.html"

    def get_render_template(self):
        return "pages/page_content_rss_feed.html"

    @property
    def get_unique_id(self):
        return "Rss" + str(self.pk)


class PageContentMap(PageContent):
    text = RichTextUploadingField(verbose_name=_("content"), blank=True)
    height = models.IntegerField(verbose_name=_("height (px)"), default=400)
    zoom = models.IntegerField(
        verbose_name=_("zoom"),
        help_text=_(
            "if not empty sets the zoom level, otherwise bounds are calculated basing upon map items"
        ),
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.page.title}/{_('map content')}"

    class Meta:
        verbose_name = _("map content block")
        verbose_name_plural = _("map content blocks")

    def class_name(self):
        return self.__class__.__name__

    def get_content_label(self):
        return _("Map")

    def get_content_description(self):
        return _("Open street map, with points, polylines, polygons and circles")

    def get_add_form_url(self):
        return reverse_lazy("admin:pages_pagecontentmap_add")

    def get_change_form_url(self):
        return reverse_lazy("admin:pages_pagecontentmap_change", args=[self.id])

    def get_delete_url(self):
        return reverse_lazy("admin:pages_pagecontentmap_delete", args=[self.id])

    def get_preview_template(self):
        return "admin/pages/page_content_map/preview.html"

    def get_render_template(self):
        return "pages/page_content_map.html"


class PageContentMapItem(models.Model):
    class Shape(models.TextChoices):
        POINT = "POINT", _("Point")
        POLYLINE = "POLYLINE", _("Polyline")
        POLYGON = "POLYGON", _("Polygon")
        CIRCLE = "CIRCLE", _("Circle")

    block = models.ForeignKey(
        PageContentMap, on_delete=models.CASCADE, related_name="items"
    )
    shape = models.CharField(
        max_length=16,
        choices=Shape.choices,
        default=Shape.POINT,
    )
    coordinates = models.TextField(_("coordinates"))
    name = models.CharField(verbose_name=_("name"), max_length=255)
    caption = models.TextField(verbose_name=_("caption"), blank=True, null=True)
    open_popup = models.BooleanField(
        _("open popup"),
        default=False,
        help_text=_("if true the popup will be immediately visible"),
    )
    link = models.CharField(
        verbose_name=_("link"), max_length=255, blank=True, null=True
    )
    color = ColorField(_("color"), default="#000000")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Map item")
        verbose_name_plural = _("Map items")


class PageContentVideo(PageContent):
    YOUTUBE = 1
    VIMEO = 2
    TWITCH = 3

    PLATFORM_CHOICES = (
        (YOUTUBE, _("Youtube")),
        (VIMEO, _("Vimeo")),
        (TWITCH, _("Twitch")),
    )

    description = RichTextUploadingField(verbose_name=_("description"), blank=True)
    credits = models.TextField(_("credits"), blank=True, null=True)
    platform = models.IntegerField(
        _("platform"), choices=PLATFORM_CHOICES, default=YOUTUBE
    )
    video_id = models.CharField(_("video id"), max_length=255)
    width_percent = models.IntegerField(
        _("width percent"), default=100, validators=[MaxValueValidator(100)]
    )

    def __str__(self):
        return f"{self.page.title}/{_('Video')}"

    class Meta:  # pyright: ignore
        verbose_name = _("Video block")
        verbose_name_plural = _("Video blocks")

    def class_name(self):
        return self.__class__.__name__

    def get_content_label(self):
        return _("Video")

    def get_content_description(self):
        return _("Video from youtube, vimeo or twitch")

    def get_add_form_url(self):
        return reverse_lazy("admin:pages_pagecontentvideo_add")

    def get_change_form_url(self):
        return reverse_lazy("admin:pages_pagecontentvideo_change", args=[self.pk])

    def get_delete_url(self):
        return reverse_lazy("admin:pages_pagecontentvideo_delete", args=[self.pk])

    def get_preview_template(self):
        return "admin/pages/page_content_video/preview.html"

    def get_render_template(self):
        return "pages/page_content_video.html"

    @property
    def get_unique_id(self):
        return "Video" + str(self.pk)


# .grid-wrapper {
#     display: grid;
#     gap: 10px;
#     grid-template-columns: 150px 100px 150px 100px ;
#     grid-template-rows: repeat(3,minmax(100px,auto));
#   }
#
#   .grid-item-1 { // id1
#     grid-column: 1 / 3;
#   }
#
#   .grid-item-2 { // id2
#     grid-column: 4 ;
#   }
#
#   .grid-item-3 { // id3
#     grid-column: 1;
#     grid-row: 2 / 4;
#   }
#   ...
#
class PageContentLayout(PageContent):
    wrapper_css = models.TextField(
        _("grid css"),
        help_text="The grid wrapper should have a .grid-wrapper class, every grid item should have a .grid-item class",
    )

    def __str__(self):
        return f"{self.page.title}/{_('Layout')}"

    def render_wrapper_css(self):
        return self.wrapper_css.replace("grid-wrapper", "grid-wrapper-" + str(self.pk))

    class Meta:  # pyright: ignore
        verbose_name = _("Layout block")
        verbose_name_plural = _("Layout blocks")

    def class_name(self):
        return self.__class__.__name__

    def get_content_label(self):
        return _("Layout")

    def get_content_description(self):
        return _("Layout with grid")

    def get_add_form_url(self):
        return reverse_lazy("admin:pages_pagecontentlayout_add")

    def get_change_form_url(self):
        return reverse_lazy("admin:pages_pagecontentlayout_change", args=[self.pk])

    def get_delete_url(self):
        return reverse_lazy("admin:pages_pagecontentlayout_delete", args=[self.pk])

    def get_preview_template(self):
        return "admin/pages/page_content_layout/preview.html"

    def get_render_template(self):
        return "pages/page_content_layout.html"

    @property
    def get_unique_id(self):
        return "Layout" + str(self.pk)


class PageContentLayoutItem(models.Model):
    TOP = 1
    BOTTOM = 2

    POSITION_CHOICES = (
        (TOP, _("Top")),
        (BOTTOM, _("Bottom")),
    )
    layout = models.ForeignKey(
        PageContentLayout, on_delete=models.CASCADE, related_name="layout_items"
    )
    css = models.TextField(
        verbose_name=_("css"),
        help_text=_(
            "Write the css class of the grid item, it must be .grid-item, i.e. .grid-item { grid-column: 1 / 3; }"
        ),
    )
    content = models.ForeignKey(
        PageContent,
        on_delete=models.CASCADE,
        related_name="layout_contents",
        blank=True,
        null=True,
        limit_choices_to={"layout_content": True},
    )
    text = RichTextUploadingField(verbose_name=_("text"), blank=True, null=True)
    text_position = models.PositiveSmallIntegerField(
        _("tex position"), choices=POSITION_CHOICES, default=TOP
    )

    class Meta:  # pyright: ignore
        verbose_name = _("Layout block item")
        verbose_name_plural = _("Layout block items")
        ordering = [
            "id",
        ]

    def render_item_css(self):
        return self.css.replace("grid-item", "grid-item-" + str(self.pk))
