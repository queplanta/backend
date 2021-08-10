import django_filters
import graphene
import graphql_geojson
from decimal import Decimal
from django.contrib.gis.geos import Polygon
from graphene.relay import Node
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphene_django.converter import convert_django_field

from db.types_revision import DocumentNode, DocumentBase
from db.graphene import CountedConnection

from .models import (
    Occurrence as OccurrenceModel,
    Suggestion as SuggestionIDModel,
    OCCURRANCE_TYPE_CHOICES, TRUNK_TYPE_CHOICES,
    CANOPY_POSITION_CHOICES, HEALTH_STATE_CHOICES
)
from accounts.models_graphql import User
from life.models_graphql import LifeNode
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode
from images.models_graphql import Image


class OccurranceType(graphene.Enum):
    NATURAL = 'natural'
    PLANTED = 'planted'

    @property
    def description(self):
        return dict(OCCURRANCE_TYPE_CHOICES)[self._value_]


class TrunkType(graphene.Enum):
    STRAIGHT = 'straight'
    BIFURCATED = 'bifurcated'
    CROOKED = 'crooked'

    @property
    def description(self):
        return dict(TRUNK_TYPE_CHOICES)[self._value_]


class CanopyPosition(graphene.Enum):
    EMERGENT = 'emergent'
    CANOPY = 'canopy'
    SUB_CANOPY = 'sub-canopy'
    SUB_FOREST = 'sub-forest'
    ISOLATED = 'isolated'

    @property
    def description(self):
        return dict(CANOPY_POSITION_CHOICES)[self._value_]


class HealthState(graphene.Enum):
    HEALTHY = 'healthy'
    DAMAGED = 'damaged'

    @property
    def description(self):
        return dict(HEALTH_STATE_CHOICES)[self._value_]


class OccurrenceCluster(graphene.ObjectType):
    count = graphene.Int()
    polygon = graphql_geojson.Geometry()
    occurrences = graphene.List(graphene.Int)


class Occurrence(DjangoObjectType, DocumentBase):
    author = graphene.Field(User)
    suggestions = DjangoConnectionField(lambda: SuggestionID)
    answer = graphene.Field(lambda: SuggestionID)
    images = DjangoConnectionField(lambda: Image)
    identity = graphene.Field(LifeNode)

    type = graphene.Field(OccurranceType)
    type_display = graphene.String()
    regional_name = graphene.String()
    cbh = graphene.Decimal()
    dbh = graphene.Decimal()
    total_height = graphene.Decimal()
    canopy_height = graphene.Decimal()
    canopy_position = graphene.Field(CanopyPosition)
    canopy_position_display = graphene.String()
    current_health_state = graphene.Field(HealthState)
    current_health_state_display = graphene.String()
    current_health_state_description = graphene.String()
    type_of_trunk = graphene.Field(TrunkType)
    type_of_trunk_display = graphene.String()
    local_population = graphene.String()

    class Meta:
        model = OccurrenceModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)
        geojson_field = 'location'
        filter_fields = []
        connection_class = CountedConnection

    @classmethod
    def get_node(cls, info, id):
        return cls._meta.model.objects.get(document_id=id)

    def resolve_author(self, info):
        return User._meta.model.objects.get(document_id=self.author_id)

    def resolve_identity(self, info):
        if not self.identity_id:
            return None
        return LifeNode._meta.model.objects.get(document_id=self.identity_id)

    def resolve_images(self, info, **kwargs):
        return Image._meta.model.objects.filter(
            document__occurrence_image=self)

    def resolve_suggestions(self, info, **kwargs):
        qs = SuggestionID._meta.model.objects.filter(
            occurrence=self.document
        )
        if self.identity_id:
            return qs.extra(
                select={'is_choosen_as_valid': "CASE WHEN identity_id = %d THEN 1 ELSE 0 END" % self.identity_id}
            ).order_by('-is_choosen_as_valid', '-document__votestats__sum_values')
        return qs.order_by('-document__votestats__sum_values')

    def resolve_type_display(self, info):
        return self.get_type_display()

    def resolve_canopy_position_display(self, info):
        return self.get_canopy_position_display()

    def resolve_current_health_state_display(self, info):
        return self.get_current_health_state_display()

    def resolve_type_of_trunk_display(self, info):
        return self.get_type_of_trunk_display()


class BoundBoxFilter(django_filters.CharFilter):
    description = "4 numbers separated by comma that represents a polygon object from the given bounding-box, e.g.: xmin,ymin,xmax,ymax)"

    def filter(self, qs, value):
        if not value:
            return qs

        bbox = [Decimal(v) for v in value.split(',')]
        geom = Polygon.from_bbox(bbox)
        return qs.filter(location__coveredby=geom)


class OccurrenceFilter(django_filters.FilterSet):
    isIdentityNull = django_filters.BooleanFilter(field_name='identity', lookup_expr='isnull')
    within_bbox = BoundBoxFilter()

    class Meta:
        model = OccurrenceModel
        fields = ['isIdentityNull', 'identity', 'author']


class SuggestionID(DjangoObjectType, DocumentBase):
    author = graphene.Field(User)
    occurrence = graphene.Field(Occurrence)
    identity = graphene.Field(LifeNode)

    class Meta:
        model = SuggestionIDModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)
        connection_class = CountedConnection

    def resolve_author(self, info):
        return User._meta.model.objects.get(document_id=self.author_id)

    def resolve_occurrence(self, info):
        return Occurrence._meta.model.objects.get(
            document_id=self.occurrence_id)

    def resolve_identity(self, info):
        return LifeNode._meta.model.objects.get(
            document_id=self.identity_id)
