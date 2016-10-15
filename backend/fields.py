import graphene

from django.utils.translation import ugettext_lazy as _


def Viewer():
    from backend.schema_queries import Query, get_default_viewer
    return graphene.Field(Query, resolver=get_default_viewer)


class Error(graphene.ObjectType):
    code = graphene.String()
    location = graphene.String()
    message = graphene.String(required=True)


def Errors():
    return graphene.List(Error)


def LoginRequiredError():
    return Error(
        code='login_required',
        message=_("You should be logged in to perform this action"),
    )


class GetBy(graphene.Field):
    def model_resolver(self, instance, args, context, info):
        try:
            return self.type._meta.model.objects.get(**args)
        except self.type._meta.model.DoesNotExist:
            return None

    def get_resolver(self, parent_resolver):
        return self.model_resolver
