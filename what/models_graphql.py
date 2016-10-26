import graphene
from graphene.relay import Node
from graphene_django import DjangoConnectionField, DjangoObjectType

from db.types_revision import DocumentRevisionBase

from .models import (
    WhatIsThis as WhatIsThisModel,
    SuggestionID as SuggestionIDModel
)
from accounts.models_graphql import User
from life.models_graphql import LifeNode
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode
from images.models_graphql import Image


class WhatIsThis(DocumentRevisionBase, VotesNode,
                 CommentsNode, DjangoObjectType):
    author = graphene.Field(User)
    suggestions = DjangoConnectionField(lambda: SuggestionID)
    images = DjangoConnectionField(lambda: Image)

    class Meta:
        model = WhatIsThisModel
        interfaces = (Node, )

    def resolve_author(self, args, context, info):
        return User._meta.model.objects.get(pk=self.author_id)

    def resolve_images(self, args, context, info):
        return Image._meta.model.objects.filter(
            document__whatisthis_image=self)


class SuggestionID(DocumentRevisionBase, VotesNode,
                   CommentsNode, DjangoObjectType):
    author = graphene.Field(User)
    whatIsThis = graphene.Field(WhatIsThis)
    identification = graphene.Field(LifeNode)

    class Meta:
        model = SuggestionIDModel
        interfaces = (Node, )

    def resolve_author(self, args, context, info):
        return User._meta.model.objects.get(pk=self.author_id)

    def resolve_whatIsThis(self, args, context, info):
        return WhatIsThis._meta.model.objects.get(pk=self.whatisthis_id)

    def resolve_identification(self, args, context, info):
        return LifeNode._meta.model.objects.get(pk=self.identification_id)
