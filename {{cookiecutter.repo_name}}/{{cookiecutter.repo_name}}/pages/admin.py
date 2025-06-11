import logging
from functools import update_wrapper


from baton.admin import RelatedDropdownFilter

from core.admin import ArchivedModelAdmin
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
{% if cookiecutter.use_translations == "y" %}from modeltranslation.admin import TranslationAdmin, TranslationStackedInline{% endif %}
from pages.admin_views import (
    EditPageContentsView,
    PageContentMapDrawerView,
    SaveContentBlocksPositionView,
)

from .forms import PageContentMapItemAdminForm, PageForm
from .models import (
    Page,
    PageContent,
    PageContentBoxItem,
    PageContentBoxMenu,
    PageContentImage,
    PageContentLayout,
    PageContentLayoutItem,
    PageContentMap,
    PageContentMapItem,
    PageContentMultiImage,
    PageContentMultiImageItem,
    PageContentRssFeed,
    PageContentText,
    PageContentTextImage,
    PageContentVideo,
)
from taggit.models import TaggedItem

logger = logging.getLogger(__name__)


@admin.register(Page)
class PageAdmin({% if cookiecutter.use_translations == "y" %}TranslationAdmin, {% endif %}ArchivedModelAdmin):  # pyright: ignore
    content_models = {}
    form = PageForm
    actions = [
        "clone",
    ]
    fieldsets = (
        (
            _("Main"),
            {
                "fields": (
                    "status",
                    "relevance",
                    "parent",
                    "url",
                    "title",
                    "image",
                    "alt_text",
                    "subject_location",
                    "tags",
                    "sites",
                    "last_updated",
                ),
                "classes": ("baton-tabs-init", "baton-tab-fs-seo", "baton-tab-fs-adv"),
            },
        ),
        (
            _("SEO"),
            {
                "classes": ("tab-fs-seo",),
                "fields": (
                    "meta_title",
                    "meta_description",
                    "meta_keywords",
                ),
            },
        ),
        (
            _("Advanced options"),
            {
                "classes": ("tab-fs-adv",),
                "fields": ("registration_required", "users", "groups", "template_name"),
            },
        ),
    )

    list_display = (
        "url",
        "title",
        "status",
        "edit_contents",
    )
    list_editable = ("status",)
    list_filter = (
        ("parent", RelatedDropdownFilter),
        "registration_required",
        "status",
    )
    filter_horizontal = (
        "users",
        "groups",
    )
    search_fields = ("url", "title")

    @admin.display(description=_("Contents"))
    def edit_contents(self, obj):
        info = self.model._meta.app_label, self.model._meta.model_name
        edit_contents_url = reverse(
            "admin:%s_%s_edit_content" % info,
            kwargs={"id": obj.id},
            current_app=self.admin_site.name,
        )
        return mark_safe(
            '<div style=""> <a class="btn btn-secondary btn-sm" href="%s"><i class="material-symbols-outlined me-2">edit</i> Modifica</a> </div>'
            % edit_contents_url
        )

    def get_urls(self):
        """
        Add the edit contents admin view
        """

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self  # pyright: ignore
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super(PageAdmin, self).get_urls()
        custom_urls = [
            path(
                "<int:id>/contents/",
                wrap(self.edit_content_view),
                name="%s_%s_edit_content" % info,
            ),
            path(
                "<int:id>/contents/save-position/",
                wrap(self.save_position),
                name="%s_%s_save_position" % info,
            ),
        ]
        return custom_urls + urls

    @csrf_exempt
    def save_position(self, request, id):
        return SaveContentBlocksPositionView.as_view()(request, id)

    def edit_content_view(self, request, id):
        return EditPageContentsView.as_view()(request, id)

    def response_post_save_add(self, request, obj):
        """
        If adding a new page, redirect to the content editing page
        """
        return redirect("admin:pages_page_edit_content", id=obj.id)

    @classmethod
    def register(cls, model):
        """
        All applications can register themself as providers of page content
        On order for translations to work properly, other applications
        should be placed after pages in installed apps

        :param page_content_module PageContentModule: the specific implementation of the PageContentModule interface
        """
        logger.debug("Registering %s" % model.__name__)
        cls.content_models.update({model.__name__: model})


class PageContentAdmin({% if cookiecutter.use_translations == "y" %}TranslationAdmin{% else %}admin.ModelAdmin{% endif %}):
    change_form_template = "admin/pages/page_content_change_form.html"

    class Media:
        css = {"all": ("pages/src/css/page_content.css",)}

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        page_id = request.GET.get("page")
        if page_id:
            page = get_object_or_404(Page, id=page_id)
        elif obj:
            page = obj.page
        else:
            page = None

        if page is None:
            messages.add_message(
                request,
                messages.WARNING,
                _(
                    "Page content block should be created starting from an already existing page."
                ),
            )
            return redirect("admin:pages_page_changelist")

        context.update(
            {"show_save_and_add_another": False, "show_delete": False, "page": page}
        )
        return super().render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            page_id = request.GET.get("page")
            page = get_object_or_404(Page, id=page_id)
            content_type = ContentType.objects.get_for_model(self.model)
            obj.page = page
            obj.content_type = content_type
            obj.position = page.content_blocks.for_content().count()  # pyright: ignore
        with transaction.atomic():  # TODO manage error
            super().save_model(request, obj, form, change)
            # we need to store the id inside the PageContent object_id field to be able to
            # retrieve specific class from the base class
            if not change:
                obj.object_id = obj.id
                obj.save()

    def response_post_save_add(self, request, obj: PageContent):
        """
        If adding  a block, redirect to the content editing page
        """
        return redirect("admin:pages_page_edit_content", id=obj.page_id)  # pyright: ignore

    def response_post_save_change(self, request, obj: PageContent):
        """
        If saving a block, redirect to the content editing page
        """
        return redirect("admin:pages_page_edit_content", id=obj.page_id)  # pyright: ignore

    def response_delete(self, request, obj_display, obj_id):
        """
        If deleting a block, redirect to the content editing page
        """
        return redirect("admin:pages_page_edit_content", id=request.POST.get("page_id"))


@admin.register(PageContentText)
class PageContentTextAdmin(PageContentAdmin):
    """Admin View for PageContentText"""

    list_display = ("id",)
    fieldsets = (
        (
            _("Main"),
            {
                "fields": (
                    "name",
                    "content",
                ),
                "classes": ("baton-tabs-init", "baton-tab-fs-adv"),
            },
        ),
        (
            _("Advanced options"),
            {
                "classes": ("tab-fs-adv",),
                "fields": (
                    "layout_content",
                    "enabled",
                    "full_width",
                    "use_accordion",
                    "show_name",
                    "background_color",
                    "text_color",
                    "url",
                ),
            },
        ),
    )


PageAdmin.register(PageContentText)


@admin.register(PageContentImage)
class PageContentImageAdmin(PageContentAdmin):
    """Admin View for PageContentImage"""

    list_display = ("id",)
    fieldsets = (
        (
            _("Main"),
            {
                "fields": (
                    "name",
                    "image",
                    "caption",
                    "credits",
                    "url",
                ),
                "classes": ("baton-tabs-init", "baton-tab-fs-adv"),
            },
        ),
        (
            _("Advanced options"),
            {
                "classes": ("tab-fs-adv",),
                "fields": (
                    "layout_content",
                    "enabled",
                    "full_width",
                    "show_captions",
                    "show_name",
                    "background_color",
                ),
            },
        ),
    )


PageAdmin.register(PageContentImage)


@admin.register(PageContentTextImage)
class PageContentTextImageAdmin(PageContentAdmin):
    """Admin View for PageContentTextImage"""

    list_display = ("id",)
    fieldsets = (
        (
            _("Main"),
            {
                "fields": (
                    "name",
                    "text",
                    "image",
                    "caption",
                    "credits",
                ),
                "classes": ("baton-tabs-init", "baton-tab-fs-adv"),
            },
        ),
        (
            _("Advanced options"),
            {
                "classes": ("tab-fs-adv",),
                "fields": (
                    "layout_content",
                    "enabled",
                    "full_width",
                    "use_accordion",
                    "show_name",
                    "background_color",
                    "image_position",
                    "show_captions",
                    "left_column_width",
                ),
            },
        ),
    )


PageAdmin.register(PageContentTextImage)


class ContentMultiImageItemInline({% if cookiecutter.use_translations == "y" %}TranslationStackedInline{% else %}admin.StackedInline{% endif %}):
    model = PageContentMultiImageItem
    extra = 1
    classes = ("collapse-entry", "expand-first")


@admin.register(PageContentMultiImage)
class PageContentMultiImageAdmin(PageContentAdmin):
    """Admin View for PageContentMultiImage"""

    list_display = ("id",)
    inlines = [ContentMultiImageItemInline]
    fieldsets = (
        (
            _("Main"),
            {
                "fields": (
                    "name",
                    "crop",
                    "crop_size",
                    "type",
                ),
                "classes": (
                    "baton-tabs-init",
                    "baton-tab-inline-images",
                    "baton-tab-fs-adv",
                ),
            },
        ),
        (
            _("Advanced options"),
            {
                "classes": ("tab-fs-adv",),
                "fields": (
                    "layout_content",
                    "enabled",
                    "full_width",
                    "height",
                    "show_captions",
                    "show_name",
                    "background_color",
                ),
            },
        ),
    )


PageAdmin.register(PageContentMultiImage)


class ContentBoxItemInline({% if cookiecutter.use_translations == "y" %}TranslationStackedInline{% else %}admin.StackedInline{% endif %}):
    model = PageContentBoxItem
    extra = 1
    classes = ("collapse-entry", "expand-first")


@admin.register(PageContentBoxMenu)
class PageContentBoxMenuAdmin(PageContentAdmin):
    """Admin View for PageContentBoxMenu"""

    list_display = ("id",)
    inlines = [ContentBoxItemInline]
    fieldsets = (
        (
            _("Main"),
            {
                "fields": (
                    "name",
                    "columns",
                    "rectangular",
                    "shadow",
                    "zoom",
                    "rounding",
                ),
                "classes": (
                    "baton-tabs-init",
                    "baton-tab-inline-images",
                    "baton-tab-fs-adv",
                ),
            },
        ),
        (
            _("Advanced options"),
            {
                "classes": ("tab-fs-adv",),
                "fields": (
                    "layout_content",
                    "enabled",
                    "full_width",
                    "show_name",
                    "background_color",
                ),
            },
        ),
    )


PageAdmin.register(PageContentBoxMenu)


@admin.register(PageContentRssFeed)
class PageContentRssFeedAdmin(PageContentAdmin):
    """Admin View for PageContentRssFeed"""

    list_display = ("id", "rss_feed_url", "num_items")
    fieldsets = (
        (
            _("Main"),
            {
                "fields": (
                    "name",
                    "rss_feed_url",
                    "num_items",
                ),
                "classes": (
                    "baton-tabs-init",
                    "baton-tab-fs-adv",
                ),
            },
        ),
        (
            _("Advanced options"),
            {
                "classes": ("tab-fs-adv",),
                "fields": (
                    "layout_content",
                    "enabled",
                    "full_width",
                    "show_name",
                    "background_color",
                ),
            },
        ),
    )


PageAdmin.register(PageContentRssFeed)


class PageContentMapItemInline({% if cookiecutter.use_translations == "y" %}TranslationStackedInline{% else %}admin.StackedInline{% endif %}):
    model = PageContentMapItem
    extra = 1
    classes = ("collapse-entry", "expand-first")
    form = PageContentMapItemAdminForm


@admin.register(PageContentMap)
class PageContentMapAdmin(PageContentAdmin):
    """Admin View for PageContentMap"""

    list_display = ("id", "name")
    inlines = [
        PageContentMapItemInline,
    ]
    fieldsets = (
        (
            _("Main"),
            {
                "fields": (
                    "name",
                    "text",
                    "height",
                    "zoom",
                ),
                "classes": (
                    "baton-tabs-init",
                    "baton-tab-inline-items",
                    "baton-tab-fs-adv",
                ),
            },
        ),
        (
            _("Advanced options"),
            {
                "classes": ("tab-fs-adv",),
                "fields": (
                    "layout_content",
                    "enabled",
                    "full_width",
                    "show_name",
                    "background_color",
                ),
            },
        ),
    )

    def get_urls(self):
        """
        Add the map drawer url
        """

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self  # pyright: ignore
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super(PageContentMapAdmin, self).get_urls()
        custom_urls = [
            path(
                "map-drawer/",
                wrap(self.map_drawer_view),
                name="%s_%s_draw" % info,
            ),
        ]
        return custom_urls + urls

    def map_drawer_view(self, request):
        return PageContentMapDrawerView.as_view()(request)


PageAdmin.register(PageContentMap)


@admin.register(PageContentVideo)
class PageContentVideoAdmin(PageContentAdmin):
    """Admin View for PageContentVideo"""

    list_display = ("id", "name")
    fieldsets = (
        (
            _("Main"),
            {
                "fields": (
                    "name",
                    "description",
                    "credits",
                    "platform",
                    "video_id",
                    "width_percent",
                ),
                "classes": (
                    "baton-tabs-init",
                    "baton-tab-fs-adv",
                ),
            },
        ),
        (
            _("Advanced options"),
            {
                "classes": ("tab-fs-adv",),
                "fields": (
                    "layout_content",
                    "enabled",
                    "full_width",
                    "show_name",
                    "background_color",
                ),
            },
        ),
    )


PageAdmin.register(PageContentVideo)


class ContentLayoutItemInline({% if cookiecutter.use_translations == "y" %}TranslationStackedInline{% else %}admin.StackedInline{% endif %}):
    model = PageContentLayoutItem
    extra = 1
    fk_name = "layout"
    classes = ("collapse-entry", "expand-first")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "content":  # Replace with your actual ForeignKey field name
            parent_id = request.resolver_match.kwargs.get(
                "object_id"
            )  # Get parent instance ID
            if parent_id:
                try:
                    parent_instance = PageContentLayout.objects.get(id=parent_id)
                    kwargs["queryset"] = PageContent.objects.filter(
                        page=parent_instance.page  # Adjust filtering based on parent model
                    )
                except PageContentLayout.DoesNotExist:
                    pass  # Fallback if the parent instance is not found
            else:
                page_id = request.GET.get("page")
                if page_id:
                    kwargs["queryset"] = PageContent.objects.filter(page_id=page_id)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(PageContentLayout)
class PageContentLayoutAdmin(PageContentAdmin):
    """Admin View for PageContentVideo"""

    list_display = ("id", "name")
    inlines = [ContentLayoutItemInline]
    fieldsets = (
        (
            _("Main"),
            {
                "fields": (
                    "name",
                    "wrapper_css",
                ),
                "classes": (
                    "baton-tabs-init",
                    "baton-tab-inline-layout_items",
                    "baton-tab-fs-adv",
                ),
            },
        ),
        (
            _("Advanced options"),
            {
                "classes": ("tab-fs-adv",),
                "fields": (
                    "layout_content",
                    "enabled",
                    "full_width",
                    "show_name",
                    "background_color",
                ),
            },
        ),
    )

    baton_form_includes = [
        ("pages/admin_includes/layout_grid.html", "wrapper_css", "right"),
        ("pages/admin_includes/layout_grid_item.html", "css", "top"),
    ]



PageAdmin.register(PageContentLayout)
