from django.db import models

class PageContentQuerySet(models.QuerySet):
    def for_content(self):
        # Define your custom filtering logic here
        return self.filter(layout_content=False, enabled=True) 

    def for_layout(self):
        # Define your custom filtering logic here
        return self.filter(layout_content=True, enabled=True) 

class PageManager(models.Manager):
    def published(self, **kwargs):
        return self.filter(status=2, **kwargs)
