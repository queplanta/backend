import graphene
from graphene import relay
from graphql_relay.node.node import from_global_id

from accounts.decorators import login_required
from db.models_graphql import Document
from backend.mutations import Mutation
from .models_graphql import Comment, Commenting


def comment_save(comment, args, request):
    comment.body = args.get('body')
    comment.save(request=request)
    return comment


CommentEdge = relay.Edge.for_node(Comment)


class CommentCreate(Mutation):
    class Input:
        parent = graphene.ID().NonNull
        body = graphene.String().NonNull

    comment = graphene.Field(CommentEdge)
    commenting = graphene.Field(Commenting)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        comment = Comment._meta.model()

        gid_type, gid = from_global_id(input.get('parent'))
        comment.parent = Document._meta.model.objects.get(pk=gid)

        comment = comment_save(comment, input, request)

        # schema = info.schema.graphene_schema
        # object_type = schema.get_type(gid_type)
        # parent = object_type(object_type.get_node(gid, request, info))

        return CommentCreate(
            comment=CommentEdge(node=comment, cursor='.'),
            commenting=Commenting.get_node(gid, info)
        )


class CommentEdit(Mutation):
    class Input:
        id = graphene.ID().NonNull
        body = graphene.String().NonNull

    comment = graphene.Field(Comment)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        comment = Comment._meta.model.objects.get(document_id=gid)
        comment = comment_save(comment, input, request)
        return CommentEdit(comment=comment)


class CommentDelete(Mutation):
    class Input:
        id = graphene.ID().NonNull

    commentDeletedID = graphene.ID().NonNull

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        gid_type, gid = from_global_id(input.get('id'))
        comment = Comment._meta.model.objects.get(document_id=gid)
        comment.delete(request=request)

        return CommentDelete(commentDeletedID=input.get('id'))
