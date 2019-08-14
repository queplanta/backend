import graphene
from graphene.relay import Node
from graphql_relay.node.node import from_global_id

from binascii import Error

from accounts.decorators import login_required
from backend.mutations import Mutation
from .models_graphql import Revision


class RevisionRevert(Mutation):
    class Input:
        id = graphene.ID(required=True)

    node = graphene.Field(Node)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
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
        current_obj.save(update_fields=['is_tip'], request=info.context)

        obj = revision.get_object()
        obj.is_tip = True
        obj.is_deleted = None
        obj.save(update_fields=['is_tip', 'is_deleted'], request=info.context)

        return RevisionRevert(
            node=obj,
        )
