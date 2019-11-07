from graphene_django import DjangoObjectType
from graphene.relay import Node

from db.types_revision import DocumentNode, DocumentBase
from db.graphene import CountedConnection

from .models import Page as PageModel
from commenting.models_graphql import CommentsNode
from images.models_graphql import ImagesNode


class Page(DjangoObjectType, DocumentBase):
    class Meta:
        model = PageModel
        interfaces = (Node, DocumentNode, CommentsNode, ImagesNode)
        filter_fields = []
        connection_class = CountedConnection

    @classmethod
    def get_node(cls, info, id):
        return cls._meta.model.objects.get(document_id=id)
