import django_filters
import graphene
import graphql_geojson
from graphene.relay import Node
from graphene_django import DjangoConnectionField, DjangoObjectType

from db.types_revision import DocumentNode, DocumentBase
from db.graphene import CountedConnection

from .models import Sowing as SowingModel
from accounts.models_graphql import User
from life.models_graphql import LifeNode
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode
from images.models_graphql import Image


class Sowing(DjangoObjectType, DocumentBase):
    author = graphene.Field(User)
    species = DjangoConnectionField(lambda: LifeNode)
    images = DjangoConnectionField(lambda: Image)

    class Meta:
        model = SowingModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)
        geojson_field = 'location'
        filter_fields = []
        connection_class = CountedConnection

    @classmethod
    def get_node(cls, info, id):
        return cls._meta.model.objects.get(document_id=id)

    def resolve_author(self, info):
        if not self.author_id:
            return None
        return User._meta.model.objects.get(document_id=self.author_id)

    def resolve_images(self, info, **kwargs):
        return Image._meta.model.objects.filter(
            document__sowing_image=self)

    def resolve_species(self, info, **kwargs):
        return LifeNode._meta.model.objects.filter(
            document__sowing_species=self)


class BoundBoxFilter(django_filters.CharFilter):
    description = "4 numbers separated by comma that represents a polygon object from the given bounding-box, e.g.: xmin,ymin,xmax,ymax)"

    def filter(self, qs, value):
        if not value:
            return qs
        # Reuse GeoJSON filter from Occurrences if needed later; keep stub here
        return qs


class SowingFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name='author')

    class Meta:
        model = SowingModel
        fields = ['author']

