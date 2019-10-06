from django.db import models
from django.contrib.contenttypes.models import ContentType

from db.models import DocumentBase, DocumentID
from db.fields import ManyToManyField

from tags.models import Tag
from images.models import limit_by_image_contenttype


def limit_by_tag_contenttype():
    try:
        ct = ContentType.objects.get_for_model(Tag)
        return {
            'content_type': ct
        }
    except ContentType.DoesNotExist:
        return {}


class Post(DocumentBase):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    body = models.TextField()

    published_at = models.DateTimeField(null=True)

    images = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_image_contenttype,
        related_name='post_image'
    )

    tags = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_tag_contenttype,
        related_name='post_tagged'
    )

    REPUTATION_VALUE = 2

    class Meta:
        unique_together = ("is_tip", "url")
        ordering = ('-published_at',)

    def __str__(self):
        return "%d: %s" % (self.revision_id, self.title) if self.revision_id else self.title
