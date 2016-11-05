import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType

from db.types_revision import DocumentRevisionBase

from .models import (
    LifeNode as LifeNodeModel,
    CommonName as CommonNameModel,
    RANK_STRING_BY_INT
)
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode


class LifeNode(DocumentRevisionBase, CommentsNode, VotesNode,
               DjangoObjectType):
    parent = graphene.Field(lambda: LifeNode)
    rank = graphene.String()
    rankDisplay = graphene.String()
    commonNames = graphene.List(graphene.String)

    class Meta:
        model = LifeNodeModel
        interfaces = (Node,)

    def resolve_parent(self, args, request, info):
        if self.parent:
            return self.parent.get_object()

    def resolve_rank(self, args, request, info):
        return RANK_STRING_BY_INT[self.rank]

    def resolve_rankDisplay(self, args, request, info):
        return self.get_rank_display()

    def resolve_commonNames(self, args, request, info):
        return CommonNameModel._meta.model.objects.filter(
            document_id__in=self.commonNames.values_list('id', flat=True)
        ).order_by('name').values_list('name', flat=True)
