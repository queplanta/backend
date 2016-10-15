import graphene
from graphene.relay import Node
from graphene_django import DjangoConnectionField, DjangoObjectType

from db.models import DocumentID
from db.types_revision import DocumentRevisionBase
from voting.models_graphql import VotesNode

from .models import Comment as CommentModel, CommentStats


class Commenting(graphene.ObjectType):
    count = graphene.Int()
    comments = DjangoConnectionField(lambda: Comment)

    class Meta:
        interfaces = (Node, )

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

    def resolve_count(self, args, context, info):
        return self.stats().count

    @classmethod
    def get_node(cls, id, context, info):
        doc = DocumentID.objects.get(pk=id)
        c = Commenting(id=doc.pk)
        c._document = doc
        return c


class CommentsNode(graphene.AbstractType):
    commenting = graphene.Field(Commenting)

    def resolve_commenting(self, args, request, info):
        c = Commenting(id=self.document.pk)
        c._document = self.document
        return c


class Comment(DocumentRevisionBase, VotesNode, CommentsNode, DjangoObjectType):
    class Meta:
        model = CommentModel
        interfaces = (Node, )
