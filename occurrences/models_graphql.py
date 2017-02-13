import graphene
from graphene.relay import Node
from graphene_django import DjangoConnectionField, DjangoObjectType

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


class Location(graphene.ObjectType):
    latitude = graphene.Float()
    longitude = graphene.Float()


class Occurrence(DocumentBase, DjangoObjectType):
    author = graphene.Field(User)
    location = graphene.Field(Location)
    location = graphene.String()
    suggestions = DjangoConnectionField(lambda: SuggestionID)
    answer = graphene.Field(lambda: SuggestionID)
    images = DjangoConnectionField(lambda: Image)

    class Meta:
        model = OccurrenceModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)

    def resolve_author(self, args, context, info):
        return User._meta.model.objects.get(document_id=self.author_id)

    def resolve_images(self, args, context, info):
        return Image._meta.model.objects.filter(
            document__occurrence_image=self)

    def resolve_suggestions(self, args, request, info):
        return SuggestionID._meta.model.objects.filter(
            occurrence=self.document
        ).order_by('revision')


class SuggestionID(DocumentBase, DjangoObjectType):
    author = graphene.Field(User)
    occurrence = graphene.Field(Occurrence)
    identity = graphene.Field(LifeNode)

    class Meta:
        model = SuggestionIDModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)

    def resolve_author(self, args, context, info):
        return User._meta.model.objects.get(document_id=self.author_id)

    def resolve_occurrence(self, args, context, info):
        return Occurrence._meta.model.objects.get(
            document_id=self.occurrence_id)

    def resolve_identity(self, args, context, info):
        return LifeNode._meta.model.objects.get(
            document_id=self.identity_id)
