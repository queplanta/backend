from django.db import models
from django.utils.text import slugify

from db.models import DocumentBase


class Tag(DocumentBase):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("is_tip", "slug")

    def save(self, *args, **kwargs):
        if len(self.slug) == 0:
            self.slug = slugify(self.title)
        return super(Tag, self).save(*args, **kwargs)
