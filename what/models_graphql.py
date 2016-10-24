import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType

from db.types_revision import DocumentRevisionBase

from .models import (
    WhatIsThis as WhatIsThisModel,
    SuggestionID as SuggestionIDModel
)
from accounts.models_graphql import User
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode


class WhatIsThis(DocumentRevisionBase, VotesNode,
                 CommentsNode, DjangoObjectType):
    author = graphene.Field(User)

    class Meta:
        model = WhatIsThisModel
        interfaces = (Node, )

    def resolve_author(self, args, context, info):
        return User._meta.model.objects.get(pk=self.author_id)


class SuggestionID(DocumentRevisionBase, VotesNode,
                   CommentsNode, DjangoObjectType):
    author = graphene.Field(User)
    whatisthis = graphene.Field(WhatIsThis)

    class Meta:
        model = SuggestionIDModel
        interfaces = (Node, )

    def resolve_author(self, args, context, info):
        return User._meta.model.objects.get(pk=self.author_id)

    def resolve_whatisthis(self, args, context, info):
            return WhatIsThis._meta.model.objects.get(pk=self.whatisthis_id)
