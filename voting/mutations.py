import graphene
from graphql_relay.node.node import from_global_id

from accounts.decorators import login_required
from db.models_graphql import Document
from backend.mutations import Mutation
from .models import Vote as VoteModel
from .models_graphql import Vote

from graphene.relay.types import Node


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

    schema = info.schema.graphene_schema
    object_type = schema.get_type(gid_type)
    parent = object_type(object_type.get_node(gid, request, info))

    return {
        'vote': vote,
        'parent': parent
    }


class VoteSet(Mutation):
    class Input:
        parent = graphene.ID().NonNull
        value = graphene.Int().NonNull

    vote = graphene.Field(Vote)
    parent = graphene.Field(Node)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        return VoteSet(**_set_vote(input, request, info))


class VoteDelete(Mutation):
    class Input:
        id = graphene.ID().NonNull

    voteDeletedID = graphene.ID().NonNull
    parent = graphene.Field(Node)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        vote = VoteModel.objects.get(document_id=gid,
                                     author=request.user.document)
        parent = vote.parent.get_object()
        vote.delete(request=request)

        object_type = None
        schema = info.schema.graphene_schema
        for obj_type_str, obj_type in schema._types_names.items():
            if hasattr(obj_type._meta, 'model'):
                if obj_type._meta.model and \
                   isinstance(parent, obj_type._meta.model):
                    object_type = obj_type

        graphql_parent = None
        if object_type:
            graphql_parent = object_type(parent)

        return VoteDelete(voteDeletedID=input.get('id'), parent=graphql_parent)
