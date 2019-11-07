import graphene
from graphene.relay import Node
from graphene_django import DjangoConnectionField, DjangoObjectType

from db.models import DocumentID
from db.types_revision import DocumentNode, DocumentBase
from db.graphene import CountedConnection

from .models import (
    Image as ImageModel,
)
from .fields import Thumbnail

from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode


class Imaging(graphene.ObjectType):
    count = graphene.Int()
    images = DjangoConnectionField(lambda: Image)

    class Meta:
        interfaces = (Node, )

    def resolve_images(self, info, **kwargs):
        return Image._meta.model.objects.filter(
            parent=self._document.pk
        ).order_by('-document__created_at')

    def resolve_count(self, info):
        return Image._meta.model.objects.filter(
            parent=self._document.pk
        ).count()

    @classmethod
    def get_node(cls, info, id):
        doc = DocumentID.objects.get(pk=id)
        c = Imaging(id=doc.pk)
        c._document = doc
        return c


class ImagesNode(graphene.Interface):
    imaging = graphene.Field(Imaging)

    def resolve_imaging(self, info):
        c = Imaging(id=self.document.pk)
        c._document = self.document
        return c


class Image(DjangoObjectType, DocumentBase):
    image = Thumbnail()

    class Meta:
        model = ImageModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)
        connection_class = CountedConnection

    def resolve_image(self, info, **kwargs):
        return self.image

    @classmethod
    def get_node(cls, info, id):
        return cls._meta.model.objects.get(document_id=id)
