import graphene
from graphql_relay.node.node import from_global_id

from accounts.decorators import login_required
from accounts.permissions import has_permission
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

    voting = Voting.get_node(info, id=gid)

    return {
        'vote': vote,
        'voting': voting
    }


class VoteSet(Mutation):
    class Input:
        parent = graphene.ID(required=True)
        value = graphene.Int(required=True)

    vote = graphene.Field(Vote)
    voting = graphene.Field(Voting)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        return VoteSet(**_set_vote(input, info.context, info))


class VoteDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    voteDeletedID = graphene.ID(required=True)
    voting = graphene.Field(Voting)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        vote = VoteModel.objects.get(document_id=gid,
                                     author=info.context.user.document)

        error = has_permission(cls, info.context, vote, 'delete')
        if error:
            return error

        parent_id = vote.parent_id
        vote.delete(request=info.context)

        voting = Voting.get_node(info, id=parent_id)

        return VoteDelete(voteDeletedID=input.get('id'), voting=voting)
