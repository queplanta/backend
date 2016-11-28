from django.db import models
from django.contrib.contenttypes.models import ContentType

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


class WhatIsThis(DocumentBase):
    subject = models.ForeignKey(DocumentID, related_name="whatisthis_subject",
                                blank=True, null=True)
    author = models.ForeignKey(DocumentID, related_name="whatisthis_author")
    images = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_image_contenttype,
        related_name='whatisthis_image'
    )
    when = models.CharField(max_length=256, blank=True, null=True)
    where = models.CharField(max_length=256, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    answer = models.ForeignKey(DocumentID, related_name="whatisthis_answer",
                               null=True, blank=True)

    REPUTATION_VALUE = 1


class SuggestionID(DocumentBase):
    whatisthis = models.ForeignKey(DocumentID,
                                   related_name="suggestion_whatisthis")
    author = models.ForeignKey(DocumentID, related_name="suggestion_author")
    identification = models.ForeignKey(DocumentID,
                                       related_name="suggestion_life")
    notes = models.TextField(blank=True, null=True)

    is_correct = models.NullBooleanField()

    REPUTATION_VALUE = 1
