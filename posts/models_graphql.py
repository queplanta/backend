from graphene_django import DjangoConnectionField, DjangoObjectType
from graphene.relay import Node

from db.types_revision import DocumentNode, DocumentBase

from .models import Post as PostModel
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode


def get_tag_type():
    from tags.models_graphql import Tag
    return Tag


class Post(DocumentBase, DjangoObjectType):
    tags = DjangoConnectionField(get_tag_type)

    class Meta:
        model = PostModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)

    def resolve_tags(self, args, request, info):
        Tag = get_tag_type()
        return Tag._meta.model.objects.filter(
            document_id__in=self.tags.values_list('id', flat=True)
        ).order_by('revision')
