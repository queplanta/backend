import graphene
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

from db.models import DocumentID
from db.types_revision import DocumentNode, DocumentBase
from db.graphene import CountedConnection
from voting.models_graphql import VotesNode

from .models import Comment as CommentModel, CommentStats


class Commenting(graphene.ObjectType):
    count = graphene.Int()
    comments = DjangoConnectionField(lambda: Comment)

    class Meta:
        interfaces = (relay.Node, )

    def resolve_comments(self, info, **kwargs):
        return Comment._meta.model.objects.filter(
            parent=self._document.pk
        ).order_by('-document__created_at')

    def stats(self):
        if not hasattr(self, '_stats'):
            self._stats, created = CommentStats.objects.get_or_create(
                document_id=self._document.pk
            )
        return self._stats

    def resolve_count(self, info):
        return self.stats().count

    @classmethod
    def get_node(cls, info, id):
        doc = DocumentID.objects.get(pk=id)
        c = Commenting(id=doc.pk)
        c._document = doc
        return c


class CommentsNode(graphene.Interface):
    commenting = graphene.Field(Commenting)

    def resolve_commenting(self, info):
        c = Commenting(id=self.document.pk)
        c._document = self.document
        return c


class Comment(DjangoObjectType, DocumentBase):
    class Meta:
        model = CommentModel
        interfaces = (relay.Node, DocumentNode, CommentsNode, VotesNode)
        filter_fields = []
        connection_class = CountedConnection

    @classmethod
    def get_node(cls, info, id):
        return cls._meta.model.objects.get(document_id=id)
