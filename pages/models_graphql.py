from graphene_django import DjangoObjectType
from graphene.relay import Node

from db.types_revision import DocumentRevisionBase

from .models import Page as PageModel
from commenting.models_graphql import CommentsNode


class Page(DocumentRevisionBase, CommentsNode, DjangoObjectType):
    class Meta:
        model = PageModel
        interfaces = (Node, )
