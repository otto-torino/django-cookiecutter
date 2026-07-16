from django.db import models
from django.db.models import Q


class PageContentQuerySet(models.QuerySet):
    def for_content(self):
        return self.filter(layout_content=False, enabled=True)

    def for_layout(self):
        return self.filter(layout_content=True, enabled=True)


class PageQuerySet(models.QuerySet):
    def published(self, **kwargs):
        return self.filter(status=2, **kwargs)

    def public(self):
        return self.published(registration_required=False)

    def for_site(self, site):
        return self.filter(sites=site)

    def accessible_by(self, user, *, site=None):
        queryset = self.for_site(site) if site is not None else self

        if (
            user is not None
            and user.is_authenticated
            and user.has_perm("pages.change_page")
        ):
            return queryset.distinct()

        queryset = queryset.published()
        if user is None or not user.is_authenticated:
            return queryset.filter(registration_required=False).distinct()

        return queryset.filter(
            Q(registration_required=False)
            | Q(registration_required=True, users=user)
            | Q(registration_required=True, groups__in=user.groups.all())
            | Q(
                registration_required=True,
                users__isnull=True,
                groups__isnull=True,
            )
        ).distinct()


class PageManager(models.Manager.from_queryset(PageQuerySet)):
    pass
