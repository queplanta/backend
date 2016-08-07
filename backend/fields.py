import graphene
from graphene.utils import with_context
from graphene.core.fields import Field
from graphene.contrib.django import DjangoConnection, DjangoConnectionField
from graphql_relay.node.node import from_global_id

from django.utils.translation import ugettext_lazy as _


def Viewer():
    from backend.schema_queries import Query, get_default_viewer
    return graphene.Field(Query, resolver=get_default_viewer)


class Error(graphene.ObjectType):
    key = graphene.String()
    message = graphene.String().NonNull


def Errors():
    return graphene.List(Error)


def LoginRequiredError():
    return Error(
        key='login_required',
        message=_("You should be logged in to perform this action"),
    )


class Connection(DjangoConnection):
    total_count = graphene.Int()

    def resolve_total_count(self, args, info):
        return len(self.get_connection_data())


class ConnectionField(DjangoConnectionField):
    @with_context
    def resolver(self, instance, args, context, info):
        resolved = super(ConnectionField, self).resolver(
            instance, args, context, info)
        resolved._set_parent(instance)
        return resolved


class GetBy(Field):
    @with_context
    def resolver(self, instance, args, context, info):
        return self.type._meta.model.objects.get(**args)


class GetByRevisionID(GetBy):
    @with_context
    def resolver(self, instance, args, context, info):
        gid_type, gid = from_global_id(args.get('id'))

        obj = self.type._meta.model.objects_revisions.get(revision_id=gid)
        obj._id_with_revision = True

        return obj
