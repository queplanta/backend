import graphene
from graphene_django import DjangoConnectionField, DjangoObjectType
from graphene.relay import Node

from db.types_revision import DocumentNode, DocumentBase
from db.graphene import CountedConnection

from .models import Post as PostModel
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode
from images.models_graphql import Image, ImagesNode


def get_tag_type():
    from tags.models_graphql import Tag
    return Tag


class Post(DjangoObjectType, DocumentBase):
    tags = DjangoConnectionField(get_tag_type)
    main_image = graphene.Field(Image)

    class Meta:
        model = PostModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode, ImagesNode)
        filter_fields = ['published_at']
        connection_class = CountedConnection

    @classmethod
    def get_node(cls, info, id):
        return cls._meta.model.objects.get(document_id=id)

    def resolve_tags(self, info, **kwargs):
        Tag = get_tag_type()
        return Tag._meta.model.objects.filter(
            document_id__in=self.tags.values_list('id', flat=True)
        ).order_by('revision')

    def resolve_main_image(self, info, **kwargs):
        if self.main_image:
            return self.main_image.get_object()
