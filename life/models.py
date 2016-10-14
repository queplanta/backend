from django.db import models
from django.utils.translation import ugettext_lazy as _
from db.models import DocumentBase, DocumentID

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
RANK_STRING_BY_INT = {v:k for k,v in RANK_BY_STRING.items()}

class LifeNode(DocumentBase):
    rank = models.IntegerField(choices=RANK_CHOICES)
    parent = models.ForeignKey(DocumentID, related_name="children", null=True)

    title = models.CharField(max_length=512)
    description = models.TextField(null=True, blank=True)
