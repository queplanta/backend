from graphene.contrib.django import DjangoNode, DjangoConnectionField
from graphene.utils import with_context

from db.types_revision import DocumentRevisionBase
from backend.fields import Connection

from .models import Tag as TagModel


class Tag(DocumentRevisionBase, DjangoNode):
    all_posts = DjangoConnectionField('Post')
    #connection_type = Connection

    class Meta:
        model = TagModel

    @with_context
    def resolve_all_posts(self, args, request, info):
        from posts.models_graphql import Post
        return Post._meta.model.objects.filter(tags=self.document).order_by('-published_at')
