import graphene
from graphql_relay.node.node import from_global_id

from accounts.decorators import login_required
from db.models_graphql import Document
from backend.mutations import Mutation
from .models import Vote as VoteModel
from .models_graphql import Vote, Voting


def _set_vote(input, request, info):
    gid_type, gid = from_global_id(input.get('parent'))
    parent = Document._meta.model.objects.get(pk=gid)

    try:
        vote = VoteModel.objects.get(parent=parent,
                                     author=request.user.document)
    except VoteModel.DoesNotExist:
        vote = VoteModel(parent=parent, author=request.user.document)

    vote.value = input.get('value')
    vote.save(request=request)

    voting = Voting.get_node(gid, info)

    return {
        'vote': vote,
        'voting': voting
    }


class VoteSet(Mutation):
    class Input:
        parent = graphene.ID().NonNull
        value = graphene.Int().NonNull

    vote = graphene.Field(Vote)
    voting = graphene.Field(Voting)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        return VoteSet(**_set_vote(input, request, info))


class VoteDelete(Mutation):
    class Input:
        id = graphene.ID().NonNull

    voteDeletedID = graphene.ID().NonNull
    voting = graphene.Field(Voting)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        vote = VoteModel.objects.get(document_id=gid,
                                     author=request.user.document)
        parent_id = vote.parent_id
        vote.delete(request=request)

        voting = Voting.get_node(parent_id, info)

        return VoteDelete(voteDeletedID=input.get('id'), voting=voting)
