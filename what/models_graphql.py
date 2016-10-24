import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType

from db.types_revision import DocumentRevisionBase

from .models import (
    WhatIsThis as WhatIsThisModel,
    SuggestionID as SuggestionIDModel
)
from accounts.models_graphql import User
from life.models_graphql import LifeNode
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode


class WhatIsThis(DocumentRevisionBase, VotesNode,
                 CommentsNode, DjangoObjectType):
    author = graphene.Field(User)
    suggestions = graphene.List(lambda: SuggestionID)

    class Meta:
        model = WhatIsThisModel
        interfaces = (Node, )

    def resolve_author(self, args, context, info):
        return User._meta.model.objects.get(pk=self.author_id)

    def resolve_suggestions(self, args, context, info):
        return SuggestionID._meta.model.objects.filter(
            whatisthis=self.document)


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
