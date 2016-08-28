import graphene
from graphene.utils import with_context
from graphene.core.fields import Field
from graphene.contrib.django import DjangoConnection

from django.utils.translation import ugettext_lazy as _


def Viewer():
    from backend.schema_queries import Query, get_default_viewer
    return graphene.Field(Query, resolver=get_default_viewer)


class Error(graphene.ObjectType):
    code = graphene.String()
    location = graphene.String()
    message = graphene.String().NonNull


def Errors():
    return graphene.List(Error)


def LoginRequiredError():
    return Error(
        code='login_required',
        message=_("You should be logged in to perform this action"),
    )


class Connection(DjangoConnection):
    total_count = graphene.Int()

    def resolve_total_count(self, args, info):
        return len(self.get_connection_data())


class GetBy(Field):
    @with_context
    def resolver(self, instance, args, context, info):
        return self.type._meta.model.objects.get(**args)
