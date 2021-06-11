from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField, DecimalRangeField

from db.models import DocumentBase, DocumentID
from db.fields import ManyToManyField, limit_by_contenttype


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


SUCCESSION_CHOICES = (
    (10, _('Primary')),
    (20, _('Secondary')),
    (30, _('Climax')),
)


THREATENED_CHOICES = (
    ('EX', _('Extinct')),
    ('EW', _('Extinct in the Wild')),
    ('CR', _('Critically Endangered')),
    ('EN', _('Endangered')),
    ('VU', _('Vulnerable')),
    ('NT', _('Near Threatened')),
    ('CD', _('Conservation Dependent')),
    ('LC', _('Least Concern')),
    ('DD', _('Data Deficient')),
    ('NE', _('Not Evaluated')),
)


COLOR_CHOICES = (
    ('white', _('White')),
    ('red', _('Red')),
    ('orange', _('Orange')),
    ('yellow', _('Yellow')),
    ('pink', _('Pink')),
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


# taken from https://plants.usda.gov/growth_habits_def.html
GROWTH_HABIT_CHOICES = (
    ('herb', _('Herb')),
    ('graminoid', _('Graminoid')),
    ('lichenous', _('Lichenous')),
    ('nonvascular', _('Nonvascular')),
    ('succulent', _('Succulent')),
    ('shrub', _('Shrub')),
    ('subshrub', _('Subshrub')),
    ('tree', _('Tree')),
    ('vine', _('Vine')),
)


PHYLLOTAXIS_CHOICES = (
    ('opposite', _('Opposite')),
    ('opposite-distichous', _('Opposite Distichous')),
    ('alternate', _('Alternate')),
    ('alternate-spiral', _('Alternate Spiral')),
    ('alternate-distichous', _('Alternate Distichous')),
    ('whorl', _('Whorl')),
    ('rosette', _('Rosette')),
)

LEAF_TYPE_CHOICES = (
    ('simple', _('Simple')),
    ('compound', _('Compound')),
    ('spine', _('Spine')),
)

LEAF_TEXTURE_CHOICES = (
    ('cartacea', _('Cartácea')),
    ('membranacea', _('Membranácea')),
    ('herbacea', _('Herbácea')),
    ('coriaceas', _('Coríaceas')),
    ('succulent', _('Succulent')),
)


GROWTH_RATE_CHOICES = (
	('slow', _('Slow')),
	('moderate', _('Moderate')),
	('fast', _('Fast')),
)


class LifeNode(DocumentBase):
    rank = models.IntegerField(choices=RANK_CHOICES)
    parent = models.ForeignKey(DocumentID, related_name="children", null=True, on_delete=models.SET_NULL)

    title = models.CharField(max_length=512)
    slug = models.SlugField(max_length=512, null=True)
    description = models.TextField(null=True, blank=True)

    edibility = models.IntegerField(null=True)

    gbif_id = models.IntegerField(null=True, blank=True)

    commonNames = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_contenttype('life.CommonName'),
        related_name='lifeNode_commonName'
    )

    images = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_contenttype('images.Image'),
        related_name='lifeNode_image'
    )

    height = DecimalRangeField(null=True)
    spread = DecimalRangeField(null=True)
    sun = DecimalRangeField(null=True)  # percentage of sun
    growth_rate = ArrayField(models.CharField(choices=GROWTH_RATE_CHOICES, max_length=25), null=True, blank=True)
    succession = models.IntegerField(null=True, choices=SUCCESSION_CHOICES)
    time_to_fruit = DecimalRangeField(null=True)

    flower_colors = ArrayField(models.CharField(choices=COLOR_CHOICES, max_length=25), null=True, blank=True)
    flower_types = ArrayField(models.CharField(choices=FLOWER_TYPES_CHOICES, max_length=45), null=True, blank=True)
    fruit_type = ArrayField(models.CharField(choices=FRUIT_TYPES_CHOICES, max_length=45), null=True, blank=True)
    growth_habit = ArrayField(models.CharField(choices=GROWTH_HABIT_CHOICES, max_length=25), null=True, blank=True)
    phyllotaxy = models.CharField(choices=PHYLLOTAXIS_CHOICES, max_length=25, null=True, blank=True)
    leaf_type = models.CharField(choices=LEAF_TYPE_CHOICES, max_length=25, null=True, blank=True)
    leaf_texture = ArrayField(models.CharField(choices=LEAF_TEXTURE_CHOICES, max_length=50), null=True, blank=True)

    threatened = models.CharField(choices=THREATENED_CHOICES, max_length=25, null=True, blank=True)
    
    # time to harvest is based on kind of usage
    # time_to_harvest = DecimalRangeField(null=True)

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
