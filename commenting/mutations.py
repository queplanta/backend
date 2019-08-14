import graphene
from graphql_relay.node.node import from_global_id
from graphql_relay.connection.arrayconnection import offset_to_cursor

from accounts.decorators import login_required
from accounts.permissions import has_permission
from db.models_graphql import Document
from backend.mutations import Mutation
from .models_graphql import Comment, Commenting


def comment_save(comment, args, request):
    comment.body = args.get('body')
    comment.save(request=request)
    return comment


class CommentCreate(Mutation):
    class Input:
        parent = graphene.ID(required=True)
        body = graphene.String(required=True)

    comment = graphene.Field(Comment._meta.connection.Edge)
    commenting = graphene.Field(Commenting)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        comment = Comment._meta.model()

        gid_type, gid = from_global_id(input.get('parent'))
        comment.parent = Document._meta.model.objects.get(pk=gid)

        comment = comment_save(comment, input, info.context)

        # schema = info.schema.graphene_schema
        # object_type = schema.get_type(gid_type)
        # parent = object_type(object_type.get_node(gid, info.context, info))

        return CommentCreate(
            comment=Comment._meta.connection.Edge(node=comment,
                                            cursor=offset_to_cursor(0)),
            commenting=Commenting.get_node(info, gid)
        )


class CommentEdit(Mutation):
    class Input:
        id = graphene.ID(required=True)
        body = graphene.String(required=True)

    comment = graphene.Field(Comment)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        comment = Comment._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, comment, 'edit')
        if error:
            return error

        comment = comment_save(comment, input, info.context)
        return CommentEdit(comment=comment)


class CommentDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    commentDeletedID = graphene.ID(required=True)
    commenting = graphene.Field(Commenting)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        comment = Comment._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, comment, 'delete')
        if error:
            return error

        parent_id = comment.parent_id
        comment.delete(request=info.context)

        return CommentDelete(
            commentDeletedID=input.get('id'),
            commenting=Commenting.get_node(info, parent_id)
        )
