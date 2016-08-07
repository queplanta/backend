from graphene.contrib.django import DjangoConnectionField
from graphene.utils import with_context

from db.types_revision import DocumentRevisionBase

from .models import Post as PostModel
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode


class Post(DocumentRevisionBase, CommentsNode, VotesNode):
    tags = DjangoConnectionField('Tag')

    class Meta:
        model = PostModel

    @with_context
    def resolve_tags(self, args, request, info):
        from tags.models_graphql import Tag
        return Tag._meta.model.objects.filter(
            document_id__in=self.tags.values_list('id', flat=True)
        ).order_by('revision')
