from django.db import models

from db.models import DocumentBase, DocumentID
from db.fields import ManyToManyField


class Tag(DocumentBase):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    class Meta:
        unique_together = ("is_tip", "slug")

    @property
    def pages(self):
        return Page.objects.filter(tags=self.document)


class Page(DocumentBase):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    tags = ManyToManyField(DocumentID, related_name='test_post_tagged')

    class Meta:
        unique_together = ("is_tip", "slug")
    # with migrations set unique_together using partial indexes
    # so we can have multiple is_tip = False values and just
    # one with is_tip = True

    def __str__(self):
        return "%d: %s" % (self.revision_id, self.title)
