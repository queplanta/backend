import datetime
import iso8601

import graphene
from graphene.types.datetime import DateTime
from graphene.relay import GlobalID, Node
from graphql.language import ast


class DocumentBase(graphene.AbstractType):
    id = GlobalID(Node, required=True)
    id_int = graphene.Int()

    my_perms = graphene.List(graphene.String)

    def resolve_id(self, args, request, info):
        if hasattr(self, '_id_with_revision'):
            return "%d:%d" % (self.document_id,
                              self.revision_id)
        return self.document_id

    def resolve_id_int(self, args, request, info):
        return self.document_id

    @classmethod
    def get_node(cls, id, context, info):
        return cls._meta.model.objects.get(document_id=id)

    def resolve_my_perms(self, args, request, info):
        return self.get_my_perms(request.user)


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
