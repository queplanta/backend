from django.db import models

from db.models import DocumentBase, DocumentID
from db.fields import ManyToManyField

from images.models import limit_by_image_contenttype


class Page(DocumentBase):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    body = models.TextField()

    images = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_image_contenttype,
        related_name='page_image'
    )

    published_at = models.DateTimeField(null=True)

    REPUTATION_VALUE = 2

    class Meta:
        unique_together = ("is_tip", "url")
        ordering = ('-published_at',)

    def __str__(self):
        return "%d: %s" % (self.revision_id, self.title) if self.revision_id else self.title
