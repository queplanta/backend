import graphene
from graphene import relay
from graphene.contrib.django import DjangoNode, DjangoConnectionField
from graphene.utils import with_context

from db.models import DocumentID
from db.types_revision import DocumentRevisionBase
from voting.models_graphql import VotesNode

from .models import Comment as CommentModel, CommentStats


class Commenting(relay.Node):
    count = graphene.Int()
    comments = DjangoConnectionField('Comment')

    @with_context
    def resolve_comments(self, args, request, info):
        return Comment._meta.model.objects.filter(
            parent=self._document.pk
        ).order_by('-document__created_at')

    def stats(self):
        if not hasattr(self, '_stats'):
            self._stats, created = CommentStats.objects.get_or_create(
                document_id=self._document.pk
            )
        return self._stats

    def resolve_count(self, args, info):
        return self.stats().count

    @classmethod
    def get_node(cls, id, info):
        doc = DocumentID.objects.get(pk=id)
        c = Commenting(id=doc.pk)
        c._document = doc
        return c


class CommentsNode(DjangoNode):
    commenting = graphene.Field(Commenting)

    class Meta:
        abstract = True

    @with_context
    def resolve_commenting(self, args, request, info):
        c = Commenting(id=self.document.pk)
        c._document = self.document
        return c


class Comment(DocumentRevisionBase, VotesNode, CommentsNode):
    class Meta:
        model = CommentModel

    @with_context
    def resolve_my_perms(self, args, request, info):
        if request.user.is_authenticated():
            if request.user.is_superuser or \
               request.user.document == self.document.revision_created.author:
                return ['edit', 'delete']
        return []
