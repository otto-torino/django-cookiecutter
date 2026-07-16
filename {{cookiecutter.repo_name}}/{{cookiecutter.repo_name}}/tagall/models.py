from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "tag"
        verbose_name_plural = "tags"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
            if kwargs.get("update_fields") is not None:
                kwargs["update_fields"] = set(kwargs["update_fields"]) | {"slug"}
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        max_length = self._meta.get_field("slug").max_length
        base_slug = (slugify(self.name) or "tag")[:max_length]
        slug = base_slug
        suffix = 2
        queryset = type(self).objects.all()
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        while queryset.filter(slug=slug).exists():
            suffix_text = f"-{suffix}"
            slug = f"{base_slug[:max_length - len(suffix_text)]}{suffix_text}"
            suffix += 1
        return slug
