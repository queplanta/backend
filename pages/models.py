from django.db import models

from db.models import DocumentBase


class Page(DocumentBase):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    body = models.TextField()

    published_at = models.DateTimeField(null=True)

    REPUTATION_VALUE = 2

    class Meta:
        unique_together = ("is_tip", "url")
        ordering = ('-published_at',)

    def __str__(self):
        return "%d: %s" % (self.revision_id, self.title) if self.revision_id else self.title
