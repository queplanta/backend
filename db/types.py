import graphene
from graphene.core.types.custom_scalars import DateTime
from graphene.relay.fields import GlobalIDField
from graphql_relay.node.node import to_global_id


class DocumentBase(graphene.ObjectType):
    id = GlobalIDField()

    my_perms = graphene.String().List

    @classmethod
    def global_id(cls, id):
        type_name = cls._meta.type_name
        return to_global_id(type_name, id)

    def to_global_id(self):
        if hasattr(self, '_id_with_revision'):
            return self.global_id("%d:%d" % (self.document_id,
                                             self.revision_id))
        return self.global_id(self.document_id)

    @classmethod
    def get_node(cls, id, info):
        return cls._meta.model.objects.get(document_id=id)


class DateTimeField(DateTime):
    pass
    # @staticmethod
    # def serialize(dt):
    #     return dt.strftime("%Y-%m-%dT%H:%M:%S")

    # @staticmethod
    # def parse_literal(node):
    #     if isinstance(node, ast.StringValue):
    #         return datetime.datetime.strptime(
    #             node.value, "%Y-%m-%dT%H:%M:%S")

    # @staticmethod
    # def parse_value(value):
    #     return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
