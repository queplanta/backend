import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType

from db.types_revision import DocumentRevisionBase

from .models import (
    Image as ImageModel,
)

from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode


class Image(DocumentRevisionBase, VotesNode,
            CommentsNode, DjangoObjectType):
    class Meta:
        model = ImageModel
        interfaces = (Node, )
