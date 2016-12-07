from graphene.relay import Node
from graphene_django import DjangoObjectType

from db.types_revision import DocumentNode, DocumentBase

from .models import (
    Image as ImageModel,
)
from .fields import Thumbnail

from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode


class Image(DocumentBase, DjangoObjectType):
    image = Thumbnail()

    class Meta:
        model = ImageModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)

    def resolve_image(self, args, request, info):
        return self.image
