from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene.relay import Node

from db.types_revision import DocumentNode, DocumentBase

from .models import Tag as TagModel


def get_post_type():
    from posts.models_graphql import Post
    return Post


class Tag(DjangoObjectType, DocumentBase):
    all_posts = DjangoConnectionField(get_post_type)

    class Meta:
        model = TagModel
        interfaces = (Node, DocumentNode)
        filter_fields = ['slug']

    def resolve_all_posts(self, info, **kwargs):
        Post = get_post_type()
        return Post._meta.model.objects.filter(
            tags=self.document).order_by('-published_at')
