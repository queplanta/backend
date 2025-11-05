from django.contrib.gis.db import models

from db.models import DocumentBase, DocumentID
from db.fields import ManyToManyField, limit_by_contenttype


class Sowing(DocumentBase):
    # Possible species contained in the sown bag
    species = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_contenttype('life.LifeNode'),
        related_name='sowing_species'
    )

    # Authenticated author (nullable); fallback to provided name/email
    author = models.ForeignKey(
        DocumentID,
        related_name="sowing_author",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    author_name = models.CharField(max_length=128, null=True, blank=True)
    author_email = models.EmailField(null=True, blank=True)

    # Attached images
    images = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_contenttype('images.Image'),
        related_name='sowing_image'
    )

    # Location fields
    location = models.PointField(geography=True, null=True)
    where = models.CharField(max_length=256, blank=True, null=True)

    # Notes
    notes = models.TextField(blank=True, null=True)

    REPUTATION_VALUE = 1

