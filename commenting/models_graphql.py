import graphene
from graphene.contrib.django import DjangoNode
from graphene.utils import with_context

from db.types_revision import DocumentRevisionBase
from backend.fields import ConnectionField
from backend.types import RelayConnection
from voting.models_graphql import VotesNode

from .models import Comment as CommentModel, CommentStats


class CommentsNode(DjangoNode):
    comments = ConnectionField('Comment')

    class Meta:
        abstract = True

    @with_context
    def resolve_comments(self, args, request, info):
        return Comment._meta.model.objects.filter(
            parent=self.document
        ).order_by('-document__created_at')


class Connection(RelayConnection):
    count = graphene.Int()

    def stats(self):
        if not hasattr(self, '_stats'):
            self._stats, created = CommentStats.objects.get_or_create(
                document_id=self._parent.document_id
            )
        return self._stats

    def resolve_count(self, args, info):
        return self.stats().count


class Comment(DocumentRevisionBase, VotesNode, CommentsNode):
    connection_type = Connection

    class Meta:
        model = CommentModel
