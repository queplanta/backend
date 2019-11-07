import django_filters
import graphene
import graphql_geojson
from graphene.relay import Node
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphene_django.converter import convert_django_field

from db.types_revision import DocumentNode, DocumentBase
from db.graphene import CountedConnection

from .models import (
    Occurrence as OccurrenceModel,
    Suggestion as SuggestionIDModel
)
from accounts.models_graphql import User
from life.models_graphql import LifeNode
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode
from images.models_graphql import Image


class Occurrence(DjangoObjectType, DocumentBase):
    author = graphene.Field(User)
    suggestions = DjangoConnectionField(lambda: SuggestionID)
    answer = graphene.Field(lambda: SuggestionID)
    images = DjangoConnectionField(lambda: Image)
    identity = graphene.Field(LifeNode)

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


class OccurrenceFilter(django_filters.FilterSet):
    isIdentityNull = django_filters.BooleanFilter(field_name='identity', lookup_expr='isnull')

    class Meta:
        model = OccurrenceModel
        fields = ['isIdentityNull', 'identity']


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
