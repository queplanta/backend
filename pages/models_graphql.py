from graphene_django import DjangoObjectType
from graphene.relay import Node

from db.types_revision import DocumentRevisionBase

from .models import Page as PageModel


class Page(DocumentRevisionBase, DjangoObjectType):
    class Meta:
        model = PageModel
        interfaces = (Node, )
