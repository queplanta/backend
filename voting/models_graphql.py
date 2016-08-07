import graphene
from graphene.contrib.django import DjangoNode
from graphene.utils import with_context
# from graphene.relay.types import Connection as RelayConnection

from db.types_revision import DocumentRevisionBase
from accounts.models_graphql import User
from backend.fields import ConnectionField
from backend.types import RelayConnection

from .models import Vote as VoteModel, VoteStats


class VotesNode(DjangoNode):
    votes = ConnectionField('Vote')

    class Meta:
        abstract = True

    @with_context
    def resolve_votes(self, args, request, info):
        return Vote._meta.model.objects.filter(
            parent=self.document
        ).order_by('-document__created_at')


class Connection(RelayConnection):
    count = graphene.Int()
    count_ups = graphene.Int()
    count_downs = graphene.Int()
    sum_values = graphene.Int()
    mine = graphene.Field('Vote')

    @with_context
    def resolve_mine(self, args, request, info):
        if not request.user.is_authenticated():
            return None

        try:
            vote = VoteModel.objects.get(
                author=request.user.document,
                parent=self._parent.document
            )
        except VoteModel.DoesNotExist:
            vote = None
        return vote

    def stats(self):
        if not hasattr(self, '_stats'):
            self._stats, created = VoteStats.objects.get_or_create(
                document_id=self._parent.document_id
            )
        return self._stats

    def resolve_count(self, args, info):
        return self.stats().count

    def resolve_count_ups(self, args, info):
        return self.stats().count_ups

    def resolve_count_downs(self, args, info):
        return self.stats().count_downs

    def resolve_sum_values(self, args, info):
        return self.stats().sum_values


class Vote(DocumentRevisionBase, DjangoNode):
    connection_type = Connection
    author = graphene.Field(User)

    class Meta:
        model = VoteModel

    def resolve_author(self, args, info):
        if self.author_id:
            return User._meta.model.objects.get(pk=self.author_id)
