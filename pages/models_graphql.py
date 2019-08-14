from graphene_django import DjangoObjectType
from graphene.relay import Node

from db.types_revision import DocumentNode, DocumentBase

from .models import Page as PageModel
from commenting.models_graphql import CommentsNode


class Page(DocumentBase, DjangoObjectType):
    class Meta:
        model = PageModel
        interfaces = (Node, DocumentNode, CommentsNode)
        filter_fields = []
