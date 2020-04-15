import django_filters
import graphene
from graphene.relay import Node
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.postgres.fields import ArrayField

from db.types_revision import DocumentNode, DocumentBase
from db.graphene import CountedConnection
from voting.models_graphql import VotesNode
from commenting.models_graphql import CommentsNode
from images.models_graphql import ImagesNode
from life.models_graphql import LifeNode

from .models import Usage as UsageModel, USAGES_CHOICES


class UsageType(graphene.Enum):
    ENERGY = 1
    DYE = 2
    FOOD = 3
    MEDICINAL = 4
    ORNAMENTAL = 5
    WOOD = 6
    OTHER = 20

    @property
    def description(self):
        return dict(USAGES_CHOICES)[self._value_]


class Usage(DjangoObjectType, DocumentBase):
    plants = DjangoConnectionField(lambda: LifeNode)
    types = graphene.List(UsageType)

    class Meta:
        model = UsageModel
        interfaces = (Node, DocumentNode, CommentsNode, ImagesNode, VotesNode)
        filter_fields = []
        connection_class = CountedConnection

    @classmethod
    def get_node(cls, info, id):
        return cls._meta.model.objects.get(document_id=id)

    def resolve_plants(self, info, **kwargs):
        return LifeNode._meta.model.objects.filter(
            document__usage_plant=self
        )


class UsagesFilter(django_filters.FilterSet):
    class Meta:
        model = UsageModel
        fields = ['plants']
        #  filter_overrides = {
        #      ArrayField: {
        #          'filter_class': django_filters.ChoiceFilter,
        #          'extra': lambda f: {
        #              'choices': USAGES_CHOICES,
        #              'lookup_expr': 'contains',
        #          },
        #      }
        #  }


class Query(object):
    plant_usages = DjangoFilterConnectionField(Usage, on='objects', filterset_class=UsagesFilter)
