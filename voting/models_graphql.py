import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType, DjangoConnectionField

from db.models import DocumentID
from db.types_revision import DocumentNode, DocumentBase
from accounts.models_graphql import User

from .models import Vote as VoteModel, VoteStats


class Voting(graphene.ObjectType):
    count = graphene.Int()
    count_ups = graphene.Int()
    count_downs = graphene.Int()
    sum_values = graphene.Int()
    mine = graphene.Field(lambda: Vote)
    votes = DjangoConnectionField(lambda: Vote)

    class Meta:
        interfaces = (Node, )

    @classmethod
    def get_node(cls, info, _id):
        doc = DocumentID.objects.get(pk=_id)
        c = Voting(id=doc.pk)
        c._document = doc
        return c

    def resolve_votes(self, info):
        return Vote._meta.model.objects.filter(
            parent_id=self._document.pk
        ).order_by('-document__created_at')

    def resolve_mine(self, info):
        if not info.context.user.is_authenticated:
            return None

        try:
            vote = VoteModel.objects.get(
                author=info.context.user.document,
                parent_id=self._document.pk
            )
        except VoteModel.DoesNotExist:
            vote = None
        return vote

    def stats(self):
        if not hasattr(self, '_stats'):
            self._stats, created = VoteStats.objects.get_or_create(
                document_id=self._document.pk
            )
        return self._stats

    def resolve_count(self, info):
        return self.stats().count

    def resolve_count_ups(self, info):
        return self.stats().count_ups

    def resolve_count_downs(self, info):
        return self.stats().count_downs

    def resolve_sum_values(self, info):
        return self.stats().sum_values


class VotesNode(graphene.Interface):
    voting = graphene.Field(Voting)

    def resolve_voting(self, info):
        c = Voting(id=self.document.pk)
        c._document = self.document
        return c


class Vote(DocumentBase, DjangoObjectType):
    author = graphene.Field(User)

    class Meta:
        model = VoteModel
        interfaces = (Node, DocumentNode)

    def resolve_author(self, info):
        if self.author_id:
            return User._meta.model.objects.get(document_id=self.author_id)
