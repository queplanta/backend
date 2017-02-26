import graphene
from graphql_relay.node.node import from_global_id

from django.utils.text import slugify

from accounts.decorators import login_required
from accounts.permissions import has_permission
from backend.mutations import Mutation
from db.models import DocumentID
from .models_graphql import List, ListItem


def list_save(list_saving, args, request):
    list_saving.title = args.get('title')
    list_saving.url = args.get('url') or slugify(list_saving.title)
    list_saving.description = args.get('description')
    list_saving.save(request=request)

    return list_saving


class ListCreate(Mutation):
    class Input:
        url = graphene.String(required=False)
        title = graphene.String(required=True)
        description = graphene.String(required=False)

    list = graphene.Field(List)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        created_list = List._meta.model()
        created_list = list_save(created_list, input, request)
        return ListCreate(list=created_list)


class ListEdit(Mutation):
    class Input:
        id = graphene.ID(required=True)
        url = graphene.String(required=False)
        title = graphene.String(required=True)
        description = graphene.String(required=False)

    list = graphene.Field(List)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        edited_list = List._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, request, edited_list, 'edit')
        if error:
            return error

        edited_list = list_save(edited_list, input, request)
        return ListEdit(post=edited_list)


class ListDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    listDeletedID = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        delete_list = List._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, request, delete_list, 'delete')
        if error:
            return error

        delete_list.delete(request=request)

        return ListDelete(listDeletedID=input.get('id'))


class ListAddItem(Mutation):
    class Input:
        list_id = graphene.ID(required=True)
        item_id = graphene.ID(required=True)
        notes = graphene.String(required=False)

    list = graphene.Field(List)
    list_item = graphene.Field(ListItem)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('list_id'))
        edited_list = List._meta.model.objects.get(document_id=gid)

        gid_type, gid = from_global_id(input.get('item_id'))
        item = DocumentID.objects.get(id=gid)

        error = has_permission(cls, request, edited_list, 'edit')
        if error:
            return error

        item_added = edited_list.add_item(item.id, input.get('notes'))
        edited_list.save(request=request)

        list_item = ListItem(
            id=item_added['id'],
            notes=item_added['notes'],
            item=item.get_object()
        )
        return ListAddItem(list=edited_list, list_item=list_item)
