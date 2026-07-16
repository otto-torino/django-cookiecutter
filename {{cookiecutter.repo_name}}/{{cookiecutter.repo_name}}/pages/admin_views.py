import json

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import View

from pages.models import Page, PageContent


class EditPageContentsView(PermissionRequiredMixin, View):
    permission_required = ["pages.add_page", "pages.change_page"]

    def get(self, request, id):
        page = get_object_or_404(Page, id=id)
        context = {
            "site_header": mark_safe(settings.BATON.get("SITE_HEADER", None)),
            "title": page.title + "/" + _("Page contents"),
            "is_popup": False,
            "has_permission": True,
            "site_url": reverse("home"),
            "page": page,
            "page_admin": admin.site._registry[Page],
        }

        return render(
            request,
            "admin/pages/change_content.html",
            context,
        )


class SaveContentBlocksPositionView(PermissionRequiredMixin, View):
    permission_required = ["pages.add_page", "pages.change_page"]

    @transaction.atomic
    def post(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        try:
            data = json.loads(request.body)
            order = data["order"]
        except (json.JSONDecodeError, KeyError, TypeError):
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        if not isinstance(order, list):
            return JsonResponse({"error": "Order must be a list."}, status=400)

        block_ids = []
        for item in order:
            block_id = item.get("id") if isinstance(item, dict) else None
            try:
                block_id = int(block_id)
            except (TypeError, ValueError):
                return JsonResponse({"error": "Invalid content block ID."}, status=400)
            if block_id in block_ids:
                return JsonResponse(
                    {"error": "Duplicate content block ID."},
                    status=400,
                )
            block_ids.append(block_id)

        blocks = {
            block.pk: block
            for block in PageContent.objects.filter(page=page, pk__in=block_ids)
        }
        if len(blocks) != len(block_ids):
            return JsonResponse(
                {"error": "A content block does not belong to this page."},
                status=400,
            )

        for position, block_id in enumerate(block_ids):
            content_block = blocks[block_id]
            content_block.position = position
            content_block.save()

        return JsonResponse({"saved": True})


class PageContentMapDrawerView(PermissionRequiredMixin, View):
    permission_required = ["pages.add_page", "pages.change_page"]

    def get(self, request):
        ctx = {
            "item_id": request.GET.get("itemId", None),
        }
        return render(request, "pages/widgets/page_content_map_drawer.html", ctx)
