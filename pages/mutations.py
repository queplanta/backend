import graphene
from graphql_relay.node.node import from_global_id

from accounts.decorators import login_required
from accounts.permissions import has_permission
from db.types import DateTimeField
from backend.mutations import Mutation
from .models_graphql import Page


def page_save(page, args, request):
    page.url = args.get('url')
    page.title = args.get('title')
    page.body = args.get('body')
    page.published_at = args.get('published_at')
    page.save(request=request)

    return page


class PageCreate(Mutation):
    class Input:
        url = graphene.String(required=True)
        title = graphene.String(required=True)
        body = graphene.String(required=True)
        published_at = DateTimeField(required=True)
        tags = graphene.String()

    page = graphene.Field(Page)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        page = Page._meta.model()
        page = page_save(page, input, request)
        return PageCreate(page=page)


class PageEdit(Mutation):
    class Input:
        id = graphene.ID(required=True)
        url = graphene.String(required=True)
        title = graphene.String(required=True)
        body = graphene.String(required=True)
        published_at = DateTimeField(required=True)
        tags = graphene.String()

    page = graphene.Field(Page)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        page = Page._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, request, page, 'edit')
        if error:
            return error

        page = page_save(page, input, request)
        return PageEdit(page=page)


class PageDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    pageDeletedID = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        page = Page._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, request, page, 'delete')
        if error:
            return error

        page.delete(request=request)

        return PageDelete(pageDeletedID=input.get('id'))
