import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType

from db.types_revision import DocumentRevisionBase

from .models import (
    LifeNode as LifeNodeModel,
    RANK_STRING_BY_INT
)
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode


class LifeNode(DocumentRevisionBase, CommentsNode, VotesNode,
               DjangoObjectType):
    parent = graphene.Field(lambda: LifeNode)
    rank = graphene.String()

    class Meta:
        model = LifeNodeModel
        interfaces = (Node,)

    def resolve_parent(self, args, request, info):
        if self.parent:
            return self.parent.get_object()

    def resolve_rank(self, args, request, info):
        return RANK_STRING_BY_INT[self.rank]
