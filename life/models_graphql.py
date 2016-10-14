import graphene
from graphene.utils import with_context

from db.types_revision import DocumentRevisionBase

from .models import (
    LifeNode as LifeNodeModel,
    RANK_STRING_BY_INT
)
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode


class LifeNode(DocumentRevisionBase, CommentsNode, VotesNode):
    parent = graphene.Field('LifeNode')
    rank = graphene.String()

    class Meta:
        model = LifeNodeModel

    @with_context
    def resolve_parent(self, args, request, info):
        if self.parent:
            return self.parent.get_object()

    @with_context
    def resolve_rank(self, args, request, info):
        return RANK_STRING_BY_INT[self.rank]
