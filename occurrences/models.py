from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField

from db.models import DocumentBase, DocumentID
from db.fields import ManyToManyField

from images.models import Image


def limit_by_image_contenttype():
    try:
        ct = ContentType.objects.get_for_model(Image)
        return {
            'content_type': ct
        }
    except ContentType.DoesNotExist:
        return {}


class Occurrence(DocumentBase):
    identity = models.ForeignKey(
        DocumentID, related_name="occurrence_identity",
        blank=True, null=True, on_delete=models.SET_NULL)
    identity_alt = models.CharField(max_length=256, blank=True, null=True)
    author = models.ForeignKey(DocumentID, related_name="occurrence_author", on_delete=models.CASCADE)
    images = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_image_contenttype,
        related_name='occurrence_image'
    )

    when = models.CharField(max_length=256, blank=True, null=True)

    location = models.PointField(geography=True, null=True)
    location_extra = JSONField(null=True)
    where = models.CharField(max_length=256, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)
    is_cultivated = models.BooleanField(default=False)

    REPUTATION_VALUE = 1


class Suggestion(DocumentBase):
    occurrence = models.ForeignKey(DocumentID,
                                   related_name="suggestion_occurrence", on_delete=models.CASCADE)
    author = models.ForeignKey(DocumentID, related_name="suggestion_author", on_delete=models.CASCADE)
    identity = models.ForeignKey(DocumentID,
                                 related_name="suggestion_identity", on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)

    is_correct = models.NullBooleanField()

    REPUTATION_VALUE = 1
