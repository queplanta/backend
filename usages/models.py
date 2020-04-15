from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from db.models import DocumentBase, DocumentID
from db.fields import ManyToManyField, limit_by_contenttype

from tags.models import Tag
from images.models import limit_by_image_contenttype


USAGE_ENERGY = 1
USAGE_DYE = 2
USAGE_FOOD = 3
USAGE_MEDICINAL = 4
USAGE_ORNAMENTAL = 5
USAGE_WOOD = 6
USAGE_OTHER = 20


USAGES_CHOICES = (
    (USAGE_FOOD, _('Food')),
    (USAGE_ORNAMENTAL, _('Ornamental')),
    (USAGE_MEDICINAL, _('Medicinal')),
    (USAGE_WOOD, _('Wood')),
    (USAGE_DYE, _('Dye')),
    (USAGE_ENERGY, _('Energy')),
    (USAGE_OTHER, _('Other')),
)

class Usage(DocumentBase):
    plants = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_contenttype('life.LifeNode'),
        related_name='usage_plant'
    )

    types = ArrayField(models.IntegerField(choices=USAGES_CHOICES))

    title = models.CharField(max_length=255)
    source = models.TextField(blank=True)
    body = models.TextField()

    images = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_contenttype('images.Image'),
        related_name='usage_image'
    )

    REPUTATION_VALUE = 1

    def __str__(self):
        return "<Usage %d: %s>" % (self.revision_id, self.title) if self.revision_id else self.title
