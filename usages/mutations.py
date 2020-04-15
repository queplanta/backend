import graphene
from graphql_relay.node.node import from_global_id

from django.utils.text import slugify

from accounts.decorators import login_required
from accounts.permissions import has_permission
from db.types import DateTimeField
from backend.mutations import Mutation
from life.models import LifeNode
from .models_graphql import Usage, UsageType


def usage_save(usage, args, request):
    usage.source = args.get('source')
    usage.title = args.get('title')
    usage.body = args.get('body')
    usage.types = args.get('types')
    usage.save(request=request)

    for plant_uid in args.get('plants'): 
        plant_gid_type, plant_gid = from_global_id(plant_uid)
        lifeNode = LifeNode.objects.get(document_id=plant_gid)
        usage.plants.add(lifeNode.document)

    return usage


class UsageCreate(Mutation):
    class Input:
        plants = graphene.List(graphene.ID, required=True)
        types = graphene.List(UsageType, required=True)
        source = graphene.String(required=False)
        title = graphene.String(required=True)
        body = graphene.String(required=True)

    usage = graphene.Field(Usage)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        usage = Usage._meta.model()
        usage = usage_save(usage, input, info.context)
        return UsageCreate(usage=usage)


class UsageEdit(Mutation):
    class Input:
        id = graphene.ID(required=True)
        plants = graphene.List(graphene.ID, required=True)
        types = graphene.List(UsageType, required=True)
        source = graphene.String(required=False)
        title = graphene.String(required=True)
        body = graphene.String(required=True)

    usage = graphene.Field(Usage)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        usage = Usage._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, usage, 'edit')
        if error:
            return error

        usage = usage_save(usage, input, info.context)
        return UsageEdit(usage=usage)


class UsageDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    usageDeletedID = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        usage = Usage._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, usage, 'delete')
        if error:
            return error

        usage.delete(request=info.context)

        return UsageDelete(usageDeletedID=input.get('id'))


class Mutations(object):
    usageCreate = UsageCreate.Field()
    usageEdit = UsageEdit.Field()
    UsageDelete = UsageDelete.Field()
