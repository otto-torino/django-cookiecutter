import json

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.http import HttpResponse
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
        data = json.loads(request.body)
        for item in data.get("order", []):
            content_block = get_object_or_404(PageContent, id=item.get("id", None))
            content_block.position = item.get("position", None)
            content_block.save()

        return HttpResponse(status=200)


class PageContentMapDrawerView(PermissionRequiredMixin, View):
    permission_required = ["pages.add_page", "pages.change_page"]

    def get(self, request):
        ctx = {
            "item_id": request.GET.get("itemId", None),
        }
        return render(request, "pages/widgets/page_content_map_drawer.html", ctx)
