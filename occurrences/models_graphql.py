import graphene
import graphql_geojson
from graphene.relay import Node
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphene_django.converter import convert_django_field

from db.types_revision import DocumentNode, DocumentBase

from .models import (
    Occurrence as OccurrenceModel,
    Suggestion as SuggestionIDModel
)
from accounts.models_graphql import User
from life.models_graphql import LifeNode
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode
from images.models_graphql import Image


class Occurrence(DocumentBase, DjangoObjectType):
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

    def resolve_author(self, info):
        return User._meta.model.objects.get(document_id=self.author_id)

    def resolve_identity(self, info):
        return LifeNode._meta.model.objects.get(document_id=self.identity_id)

    def resolve_images(self, info, **kwargs):
        return Image._meta.model.objects.filter(
            document__occurrence_image=self)

    def resolve_suggestions(self, info, **kwargs):
        return SuggestionID._meta.model.objects.filter(
            occurrence=self.document
        ).order_by('-document__votestats__sum_values')


class SuggestionID(DocumentBase, DjangoObjectType):
    author = graphene.Field(User)
    occurrence = graphene.Field(Occurrence)
    identity = graphene.Field(LifeNode)

    class Meta:
        model = SuggestionIDModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)

    def resolve_author(self, info):
        return User._meta.model.objects.get(document_id=self.author_id)

    def resolve_occurrence(self, info):
        return Occurrence._meta.model.objects.get(
            document_id=self.occurrence_id)

    def resolve_identity(self, info):
        return LifeNode._meta.model.objects.get(
            document_id=self.identity_id)
