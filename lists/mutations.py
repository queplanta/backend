import graphene
from graphql_relay.node.node import from_global_id
from graphql_relay.connection.arrayconnection import offset_to_cursor

from django.utils.text import slugify

from accounts.decorators import login_required
from accounts.permissions import has_permission
from backend.mutations import Mutation
from db.models import DocumentID
from life.models import LifeNode as LifeNodeModel
from life.models_graphql import LifeNode
from .models_graphql import List, ListItem, CollectionItem, WishItem


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
    def mutate_and_get_payload(cls, root, info, **input):
        created_list = List._meta.model()
        created_list = list_save(created_list, input, info.context)
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
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        edited_list = List._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, edited_list, 'edit')
        if error:
            return error

        edited_list = list_save(edited_list, input, info.context)
        return ListEdit(post=edited_list)


class ListDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    listDeletedID = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        delete_list = List._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, delete_list, 'delete')
        if error:
            return error

        delete_list.delete(request=info.context)

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
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('list_id'))
        edited_list = List._meta.model.objects.get(document_id=gid)

        gid_type, gid = from_global_id(input.get('item_id'))
        item = DocumentID.objects.get(id=gid)

        error = has_permission(cls, info.context, edited_list, 'edit')
        if error:
            return error

        item_added = edited_list.add_item(item.id, input.get('notes'))
        edited_list.save(request=info.context)

        list_item = ListItem(
            id=item_added['id'],
            notes=item_added['notes'],
            item=item.get_object()
        )
        return ListAddItem(list=edited_list, list_item=list_item)


class CollectionItemAdd(Mutation):
    class Input:
        plant_id = graphene.ID(required=True)

    collection_item = graphene.Field(CollectionItem._meta.connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('plant_id'))
        life_node = LifeNodeModel.objects.get(document_id=gid)

        CollectionItemModel = CollectionItem._meta.model

        collection_item = CollectionItemModel(
            plant=life_node.document,
            user=info.context.user.document
        )
        collection_item.save(request=info.context)

        return CollectionItemAdd(
            collection_item=CollectionItem._meta.connection.Edge(
                node=collection_item,
                cursor=offset_to_cursor(0)
            )
        )


class CollectionItemDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    deleted_id = graphene.ID(required=True)
    life_node = graphene.Field(LifeNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        collection_item = CollectionItem._meta.model.objects.get(document_id=gid)
        life_node = LifeNodeMode.objects.get(document_id=collection_item.plant_id)
        collection_item.delete(request=info.context)

        return CollectionItemDelete(
            deleted_id=input.get('id'),
            life_node=life_node
        )


class WishItemAdd(Mutation):
    class Input:
        plant_id = graphene.ID(required=True)

    wish_item = graphene.Field(WishItem._meta.connection.Edge)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('plant_id'))
        life_node = LifeNodeModel.objects.get(document_id=gid)

        WishItemModel = WishItem._meta.model

        wish_item = WishItemModel(
            plant=life_node.document,
            user=info.context.user.document
        )
        wish_item.save(request=info.context)

        return WishItemAdd(
            wish_item=WishItem._meta.connection.Edge(
                node=wish_item,
                cursor=offset_to_cursor(0)
            )
        )


class WishItemDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    deleted_id = graphene.ID(required=True)
    life_node = graphene.Field(LifeNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        wish_item = WishItem._meta.model.objects.get(document_id=gid)
        life_node = LifeNodeMode.objects.get(document_id=collection_item.plant_id)
        wish_item.delete(request=info.context)

        return WishItemDelete(
            deleted_id=input.get('id'),
            life_node=life_node
        )


class Mutations(object):
    list_create = ListCreate.Field()
    list_edit = ListEdit.Field()
    list_delete = ListDelete.Field()
    list_add_item = ListAddItem.Field()

    collection_item_add = CollectionItemAdd.Field()
    collection_item_delete = CollectionItemDelete.Field()

    wish_item_add = WishItemAdd.Field()
    wish_item_delete = WishItemDelete.Field()
