from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify

from db.models import DocumentBase, DocumentID
from db.fields import ManyToManyField

from images.models import limit_by_image_contenttype


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

COLOR_CHOICES = (
    ('white', _('White')),
    ('red', _('Red')),
    ('orange', _('Orange')),
    ('yellow', _('Yellow')),
    ('pink', _('Pink')),
    ('pink-lilac', _('Pink Lilac')),
    ('lilac', _('Lilac')),
    ('blue', _('Blue')),
    ('light-blue', _('Light Blue')),
    ('green', _('Green')),
    ('purple', _('Purple')),
    ('black', _('Black')),
    ('brown', _('Brown')),
    ('nut-brown', _('Nut Brown')),
    ('wine', _('Wine')),
    ('cream', _('Cream')),
)

FLOWER_TYPES_CHOICES = (
    ('inflorescence', _('Inflorescence')),
    ('pseudanthium', _('Composite Flower')),
    ('solitary', _('Solitary Flower')),
)

# taken from https://courses.botany.wisc.edu/botany_400/Lab/LabWK03Fruitkey.html
FRUIT_TYPES_CHOICES = (
    ('simple', _('Simple')),
        ('dry', _('Dry')),
            ('dehiscent', _('Dehiscent')),
            ('legume', _('Legume')),
            ('follicle', _('Follicle')),
            ('capsule', _('Capsule')),
                ('capsule-loculicidal', _('Loculicidal Capsule')),
                ('capsule-septicidal', _('Septicidal Capsule')),
                ('capsule-silique', _('Silique Capsule')),
                ('capsule-silicle', _('Silicle Capsule')),
                ('capsule-pyxis', _('Pyxis Capsule')),
                ('capsule-poricidal', _('Poricidal Capsule')),
            ('indehiscent', _('Indehiscent')),
                ('achene', _('Achene')),
                ('nut', _('Nut')),
                ('samara', _('Samara')),
                ('grain', _('Grain')),
                ('schizocarp', _('Schizocarp')),
    ('fleshy', _('Fleshy')),
        ('drupe', _('Drupe')),
        ('berry', _('Berry')),
            ('hesperidium', _('Hesperidium')),
            ('pepo', _('Pepo')),
        ('pome', _('Pome')),
    ('aggregate', _('Aggregate')),
    ('multiple', _('Multiple')),
)

def limit_by_commonName_contenttype():
    try:
        ct = ContentType.objects.get_for_model(CommonName)
        return {
            'content_type': ct
        }
    except ContentType.DoesNotExist:
        return {}


class LifeNode(DocumentBase):
    rank = models.IntegerField(choices=RANK_CHOICES)
    parent = models.ForeignKey(DocumentID, related_name="children", null=True, on_delete=models.SET_NULL)

    title = models.CharField(max_length=512)
    slug = models.SlugField(max_length=512, null=True)
    description = models.TextField(null=True, blank=True)

    edibility = models.IntegerField(null=True)
    flower_colors = ArrayField(models.CharField(choices=COLOR_CHOICES, max_length=25), null=True, blank=True)
    flower_types = ArrayField(models.CharField(choices=FRUIT_TYPES_CHOICES, max_length=45), null=True, blank=True)

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
    country = models.CharField(max_length=3, null=True, blank=True)
    region = models.CharField(max_length=3, null=True, blank=True)

    REPUTATION_VALUE = 1


class Characteristic(DocumentBase):
    tag = models.ForeignKey(DocumentID, related_name="characteristic_tag", on_delete=models.CASCADE)
    lifeNode = models.ForeignKey(DocumentID,
                                 related_name="characteristic_lifeNode", on_delete=models.CASCADE)
    value = models.CharField(max_length=512, null=True)

    def _get_tag(self):
        if not hasattr(self, '_tag'):
            self._tag = self.tag.get_object()
        return self._tag
