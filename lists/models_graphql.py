from graphene_django import DjangoObjectType
from graphene.relay import Node

from db.types_revision import DocumentNode, DocumentBase

from .models import List as ListModel
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode


class List(DocumentBase, DjangoObjectType):
    class Meta:
        model = ListModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)
