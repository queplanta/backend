from django.db import models
from django.contrib.contenttypes.models import ContentType

from db.models import DocumentBase, DocumentID
from db.fields import ManyToManyField, limit_by_contenttype

from tags.models import Tag


class Post(DocumentBase):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    body = models.TextField()
    summary = models.TextField(blank=True, default="")

    published_at = models.DateTimeField(null=True)

    images = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_contenttype('images.Image'),
        related_name='post_image'
    )
    main_image = models.ForeignKey(
        DocumentID,
        limit_choices_to=limit_by_contenttype('images.Image'),
        related_name='post_main_image',
        null=True,
        on_delete=models.SET_NULL
    )

    tags = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_contenttype('tags.Tag'),
        related_name='post_tagged'
    )

    REPUTATION_VALUE = 2

    class Meta:
        unique_together = ("is_tip", "url")
        ordering = ('-published_at',)

    def __str__(self):
        return "%d: %s" % (self.revision_id, self.title)
