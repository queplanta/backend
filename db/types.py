import datetime
import iso8601

import graphene
from graphene.types.datetime import DateTime
from graphene.relay import GlobalID, Node
from graphql.language import ast


class MyGlobalID(GlobalID):
    @staticmethod
    def resolve_id(root, info, **args):
        if hasattr(root, '_id_with_revision'):
            return "%d:%d" % (root.document_id,
                              root.revision_id)
        return root.document_id

    @staticmethod
    def id_resolver(parent_resolver, node, root, info, parent_type_name=None, **args):
        type_id = MyGlobalID.resolve_id(root, info, **args)
        parent_type_name = parent_type_name or info.parent_type.name
        return node.to_global_id(parent_type_name, type_id)  # root._meta.name


class DocumentBase(graphene.AbstractType):
    id = MyGlobalID(Node, required=True)
    id_int = graphene.Int()

    my_perms = graphene.List(graphene.String)

    def resolve_id_int(self, info):
        return self.document_id

    @classmethod
    def get_node(cls, info, id):
        return cls._meta.model.objects.get(document_id=id)

    def resolve_my_perms(self, info):
        return self.get_my_perms(info.context.user)


class DateTimeField(DateTime):
    @staticmethod
    def serialize(dt):
        assert isinstance(dt, (datetime.datetime, datetime.date)), (
            'Received not compatible datetime "{}"'.format(repr(dt))
        )
        return dt.isoformat()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return iso8601.parse_date(node.value)

    @staticmethod
    def parse_value(value):
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
