import graphene
from graphql_relay.node.node import from_global_id

from django.utils.text import slugify

from accounts.decorators import login_required
from accounts.permissions import has_permission
from db.models_graphql import Document
from backend.mutations import Mutation
from .models_graphql import LifeNode
from .models import RANK_BY_STRING


def node_save(node, args, request):
    node.title = args.get('title')
    node.description = args.get('description')
    node.rank = RANK_BY_STRING[args.get('rank')]

    parent_id = args.get('parent')
    if parent_id:
        gid_type, gid = from_global_id(parent_id)
        node.parent = Document._meta.model.objects.get(pk=gid)

    node.save(request=request)
    return node


class LifeNodeCreate(Mutation):
    class Input:
        title = graphene.String().NonNull
        description = graphene.String()
        rank = graphene.String().NonNull
        parent = graphene.ID()

    lifeNode = graphene.Field(LifeNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        node = LifeNode._meta.model()
        node = node_save(node, input, request)
        return LifeNodeCreate(lifeNode=node)


class LifeNodeEdit(Mutation):
    class Input:
        id = graphene.ID().NonNull
        title = graphene.String().NonNull
        description = graphene.String().NonNull
        rank = graphene.String().NonNull
        parent = graphene.ID().NonNull

    lifeNode = graphene.Field(LifeNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        node = LifeNode._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, request, node, 'edit')
        if error:
            return error

        node = node_save(node, input, request)
        return LifeNodeEdit(lifeNode=node)


class LifeNodeDelete(Mutation):
    class Input:
        id = graphene.ID().NonNull

    lifeNodeDeletedID = graphene.ID().NonNull

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        node = LifeNode._meta.model.objects.get(document_id=gid)
        
        error = has_permission(cls, request, node, 'delete')
        if error:
            return error

        node.delete(request=request)

        return LifeNodeDelete(lifeNodeDeletedID=input.get('id'))
