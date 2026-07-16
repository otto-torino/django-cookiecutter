from typing import cast

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import quote
from django.db import transaction
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html, format_html_join
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
{% if cookiecutter.use_translations == 'y' %}from modeltranslation.admin import TranslationAdmin{% endif %}

from .models import Tag


class MergeTagsForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),
        widget=forms.MultipleHiddenInput,
    )
    target_tag = forms.ModelChoiceField(queryset=Tag.objects.none(), empty_label=None)

    def __init__(self, *args, **kwargs):
        tags_queryset = kwargs.pop("tags_queryset")
        super().__init__(*args, **kwargs)
        ordered_tags_queryset = tags_queryset.order_by("pk")
        tags_field = cast(forms.ModelMultipleChoiceField, self.fields["tags"])
        tags_field.queryset = ordered_tags_queryset
        target_tag_field = cast(forms.ModelChoiceField, self.fields["target_tag"])
        target_tag_field.queryset = ordered_tags_queryset

    def clean_target_tag(self):
        target_tag = self.cleaned_data["target_tag"]
        tags = self.cleaned_data.get("tags")
        if tags is not None and not tags.filter(pk=target_tag.pk).exists():
            raise forms.ValidationError("Select a tag to keep among the selected tags.")
        return target_tag


@admin.register(Tag)
class TagAdmin({% if cookiecutter.use_translations == 'y' %}TranslationAdmin{% else %}admin.ModelAdmin{% endif %}):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    readonly_fields = ("used_by",)
    prepopulated_fields = {"slug": ("name",)}
    actions = ("merge_tags",)
    used_by_limit = 50

    @admin.display(description=_("Used by"))
    def used_by(self, obj):
        if not obj or not obj.pk:
            return "-"

        sections = []
        for relation in Tag._meta.related_objects:
            if not relation.many_to_many:
                continue

            accessor_name = relation.get_accessor_name()
            if not accessor_name:
                continue

            queryset = getattr(obj, accessor_name).all().order_by("pk")
            total = queryset.count()
            if not total:
                continue

            related_model = relation.related_model
            related_items = [
                self._format_related_object_link(item)
                for item in queryset[: self.used_by_limit]
            ]
            remaining = total - len(related_items)
            if remaining:
                related_items.append(
                    format_html(
                        "<li>{}</li>",
                        _("+ %(count)s more") % {"count": remaining},
                    )
                )

            sections.append(
                format_html(
                    "<div><strong>{} ({})</strong><ul>{}</ul></div>",
                    capfirst(related_model._meta.verbose_name_plural),
                    total,
                    format_html_join("", "{}", ((item,) for item in related_items)),
                )
            )

        if not sections:
            return "-"
        return format_html_join("", "{}", ((section,) for section in sections))

    def _format_related_object_link(self, obj):
        opts = obj._meta
        if opts.model in self.admin_site._registry:
            try:
                url = reverse(
                    "admin:%s_%s_change" % (opts.app_label, opts.model_name),
                    args=(quote(obj.pk),),
                )
                return format_html('<li><a href="{}">{}</a></li>', url, obj)
            except NoReverseMatch:
                pass
        return format_html("<li>{}</li>", obj)

    def _render_merge_tags_form(self, request, form, queryset):
        admin_form = helpers.AdminForm(
            form,
            [(None, {"fields": ["target_tag"]})],
            {},
            (),
            model_admin=self,
        )
        context = dict(
            self.admin_site.each_context(request),
            title=_("Merge tags"),
            subtitle=None,
            adminform=admin_form,
            form=form,
            queryset=queryset,
            action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
            opts=self.model._meta,
            original=_("Merge tags"),
            object_id=None,
            is_popup=False,
            to_field=None,
            media=self.media + admin_form.media,
            inline_admin_formsets=[],
            errors=helpers.AdminErrorList(form, []),
            preserved_filters=self.get_preserved_filters(request),
            has_view_permission=self.has_view_permission(request),
            has_add_permission=self.has_add_permission(request),
            has_change_permission=self.has_change_permission(request),
            has_delete_permission=self.has_delete_permission(request),
            has_editable_inline_admin_formsets=False,
            save_as=False,
            save_on_top=False,
            add=False,
            change=False,
            show_save=True,
            show_save_and_add_another=False,
            show_save_and_continue=False,
            show_close=False,
            show_delete=False,
        )
        return TemplateResponse(request, "admin/tagall/merge_tags.html", context)

    @admin.action(description=_("Merge selected tags"))
    def merge_tags(self, request, queryset):
        if "apply" in request.POST:
            selected_tag_ids = request.POST.getlist("tags")
            queryset = Tag.objects.filter(pk__in=selected_tag_ids).order_by("pk")
        else:
            queryset = queryset.order_by("pk")

        if queryset.count() < 2:
            self.message_user(
                request,
                _("Select at least two tags to merge."),
                level=messages.ERROR,
            )
            return

        form = MergeTagsForm(
            request.POST if "apply" in request.POST else None,
            tags_queryset=queryset,
            initial={"tags": queryset, "target_tag": queryset.first()},
        )
        if "apply" not in request.POST or not form.is_valid():
            return self._render_merge_tags_form(request, form, queryset)

        tags = form.cleaned_data["tags"].order_by("pk")
        target_tag = form.cleaned_data["target_tag"]
        source_tags = tags.exclude(pk=target_tag.pk)
        moved_relations = 0

        with transaction.atomic():
            for relation in Tag._meta.related_objects:
                if not relation.many_to_many:
                    continue

                through = relation.through
                tag_field = relation.field.m2m_reverse_field_name()
                obj_attname = through._meta.get_field(
                    relation.field.m2m_field_name()
                ).attname
                source_qs = through.objects.filter(
                    **{f"{tag_field}__in": source_tags}
                )
                already_linked = through.objects.filter(
                    **{tag_field: target_tag}
                ).values(obj_attname)
                moved_relations += source_qs.exclude(
                    **{f"{obj_attname}__in": already_linked}
                ).update(**{tag_field: target_tag})
                source_qs.delete()

            merged_count = source_tags.count()
            source_tags.delete()

        self.message_user(
            request,
            _("Merged %(count)s tags into “%(tag)s”. Processed %(relations)s relations.")
            % {
                "count": merged_count + 1,
                "tag": target_tag.name,
                "relations": moved_relations,
            },
            level=messages.SUCCESS,
        )
