from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene.relay import Node

from db.types_revision import DocumentRevisionBase

from .models import Tag as TagModel


def get_post_type():
    from posts.models_graphql import Post
    return Post


class Tag(DocumentRevisionBase, DjangoObjectType):
    all_posts = DjangoConnectionField(get_post_type)

    class Meta:
        model = TagModel
        interfaces = (Node, )

    def resolve_all_posts(self, args, request, info):
        Post = get_post_type()
        return Post._meta.model.objects.filter(
            tags=self.document).order_by('-published_at')
