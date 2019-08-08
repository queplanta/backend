import graphene
from graphql_relay.node.node import from_global_id

from accounts.decorators import login_required
from accounts.permissions import has_permission
from backend.mutations import Mutation
from .models_graphql import Tag


def tag_save(tag, args, request):
    tag.slug = args.get('slug')
    tag.title = args.get('title')
    tag.description = args.get('description')
    tag.save(request=request)
    return tag


class TagCreate(Mutation):
    class Input:
        slug = graphene.String(required=True)
        title = graphene.String(required=True)
        description = graphene.String()

    tag = graphene.Field(Tag)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        tag = Tag._meta.model()
        tag = tag_save(tag, input, info.context)
        return TagCreate(tag=tag)


class TagEdit(Mutation):
    class Input:
        id = graphene.ID(required=True)
        slug = graphene.String(required=True)
        title = graphene.String(required=True)
        description = graphene.String()

    tag = graphene.Field(Tag)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        tag = Tag._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, tag, 'edit')
        if error:
            return error

        tag = tag_save(tag, input, info.context)
        return TagEdit(tag=tag)


class TagDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    tagDeletedID = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        tag = Tag._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, tag, 'delete')
        if error:
            return error

        tag.delete(request=info.context)

        return TagDelete(tagDeletedID=input.get('id'))
