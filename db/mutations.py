import graphene
# from graphene import relay
from graphene.relay.types import Node
from graphql_relay.node.node import from_global_id

from binascii import Error

from accounts.decorators import login_required
from backend.mutations import Mutation
from .models_graphql import Revision


class RevisionRevert(Mutation):
    class Input:
        id = graphene.ID().NonNull

    # commentDeletedID = graphene.ID().NonNull
    # commenting = graphene.Field(Commenting)
    node = graphene.Field(Node)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        try:
            gid_type, gid = from_global_id(input.get('id'))
        except Error:
            gid = input.get('id')

        revision = Revision._meta.model.objects.get(id=gid)

        document = revision.document

        current_obj = document.get_object()

        document.revision_tip_id = revision.pk
        document.save(update_fields=['revision_tip_id'])

        current_obj.is_tip = None
        current_obj.save(update_fields=['is_tip'], request=request)

        obj = revision.get_object()
        obj.is_tip = True
        obj.is_deleted = None
        obj.save(update_fields=['is_tip', 'is_deleted'], request=request)

        object_type = None
        schema = info.schema.graphene_schema
        for obj_type_str, obj_type in schema._types_names.items():
            if hasattr(obj_type._meta, 'model'):
                if obj_type._meta.model and \
                   isinstance(obj, obj_type._meta.model):
                    object_type = obj_type

        graphql_parent = None
        if object_type:
            graphql_parent = object_type(obj)

        return RevisionRevert(
            node=graphql_parent,
            # commentDeletedID=input.get('id'),
            # commenting=Commenting.get_node(parent_id, info)
        )
