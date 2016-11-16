from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify

from db.models import DocumentBase, DocumentID
from db.fields import ManyToManyField

from images.models import Image


RANK_KINGDOM = 10
RANK_PHYLUM = 20
RANK_CLASS = 30
RANK_ORDER = 40
RANK_FAMILY = 50
RANK_GENUS = 60
RANK_SPECIES = 70
RANK_INFRASPECIES = 80
RANK_VARIETY = 100

RANK_CHOICES = (
    (RANK_KINGDOM, _('Kingdom')),
    (RANK_PHYLUM, _('Phylum')),
    (RANK_CLASS, _('Class')),
    (RANK_ORDER, _('Order')),
    (RANK_FAMILY, _('Family')),
    (RANK_GENUS, _('Genus')),
    (RANK_SPECIES, _('Species')),
    (RANK_INFRASPECIES, _('Infraspecies')),
    (RANK_VARIETY, _('Variety')),
)

RANK_BY_STRING = {
    'kingdom': RANK_KINGDOM,
    'phylum': RANK_PHYLUM,
    'class': RANK_CLASS,
    'order': RANK_ORDER,
    'family': RANK_FAMILY,
    'genus': RANK_GENUS,
    'species': RANK_SPECIES,
    'infraspecies': RANK_INFRASPECIES,
    'variety': RANK_VARIETY,
}
RANK_STRING_BY_INT = {v: k for k, v in RANK_BY_STRING.items()}


def limit_by_commonName_contenttype():
    try:
        ct = ContentType.objects.get_for_model(CommonName)
        return {
            'content_type': ct
        }
    except ContentType.DoesNotExist:
        return {}


def limit_by_image_contenttype():
    try:
        ct = ContentType.objects.get_for_model(Image)
        return {
            'content_type': ct
        }
    except ContentType.DoesNotExist:
        return {}


class LifeNode(DocumentBase):
    rank = models.IntegerField(choices=RANK_CHOICES)
    parent = models.ForeignKey(DocumentID, related_name="children", null=True)

    title = models.CharField(max_length=512)
    slug = models.SlugField(max_length=512, null=True)
    description = models.TextField(null=True, blank=True)

    gbif_id = models.IntegerField(null=True, blank=True)

    commonNames = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_commonName_contenttype,
        related_name='lifeNode_commonName'
    )

    images = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_image_contenttype,
        related_name='lifeNode_image'
    )

    # class Meta:
    #     unique_together = ("is_tip", "slug")

    def save(self, *args, **kwargs):
        if not self.slug or len(self.slug) == 0:
            self.slug = slugify(self.title)
        return super(LifeNode, self).save(*args, **kwargs)


class CommonName(DocumentBase):
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=255, null=True, blank=True)
