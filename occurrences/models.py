from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _

from db.models import DocumentBase, DocumentID
from db.fields import ManyToManyField, limit_by_contenttype

from images.models import Image


OCCURRANCE_TYPE_CHOICES = (
    ('natural', _('Natural')),
    ('planted', _('Planted')),
)

TRUNK_TYPE_CHOICES = (
    ('straight', _('Straight')),
    ('bifurcated', _('Bifurcated')),
    ('crooked', _('Crooked')),
)

CANOPY_POSITION_CHOICES = (
    ('emergent', _('Emergent')),
    ('canopy', _('Canopy')),
    ('sub-canopy', _('Sub-canopy')),
    ('sub-forest', _('Sub-forest')),
    ('isolated', _('Isolated')),
)

HEALTH_STATE_CHOICES = (
    ('healthy', _('Healthy')),
    ('damaged', _('Damaged')),
)


class Occurrence(DocumentBase):
    identity = models.ForeignKey(
        DocumentID, related_name="occurrence_identity",
        blank=True, null=True, on_delete=models.SET_NULL)
    identity_alt = models.CharField(max_length=256, blank=True, null=True)
    author = models.ForeignKey(DocumentID, related_name="occurrence_author", on_delete=models.CASCADE)
    images = ManyToManyField(
        DocumentID,
        limit_choices_to=limit_by_contenttype('images.Image'),
        related_name='occurrence_image'
    )

    when = models.CharField(max_length=256, blank=True, null=True)

    location = models.PointField(geography=True, null=True)
    location_extra = JSONField(null=True)
    where = models.CharField(max_length=256, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)
    is_request = models.BooleanField(default=False)

    # plant nursery fields
    type = models.CharField(choices=OCCURRANCE_TYPE_CHOICES, max_length=25, null=True, blank=True)
    regional_name = models.CharField(max_length=255, null=True, blank=True)
    cbh = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text=_("Circumference at breast height"))
    dbh = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text=_("Diameter at breast height"))
    total_height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    canopy_height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    canopy_position = models.CharField(choices=CANOPY_POSITION_CHOICES, max_length=25, null=True, blank=True)
    current_health_state = models.CharField(choices=HEALTH_STATE_CHOICES, max_length=25, null=True, blank=True)
    current_health_state_description = models.TextField(blank=True, null=True)
    type_of_trunk = models.CharField(choices=TRUNK_TYPE_CHOICES, max_length=25, null=True, blank=True)
    local_population = models.TextField(blank=True, null=True)

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
