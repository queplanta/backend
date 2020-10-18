import graphene
from graphql_relay.node.node import from_global_id

from django.utils.text import slugify

from accounts.decorators import login_required
from accounts.permissions import has_permission
from db.types import DateTimeField
from db.models_graphql import Document
from backend.mutations import Mutation
from .models_graphql import Post


def post_save(post, args, request):
    post.url = args.get('url')
    post.title = args.get('title')
    post.body = args.get('body')
    post.summary = args.get('summary')
    post.published_at = args.get('published_at')

    image_id = args.get('main_image')
    if image_id:
        gid_type, gid = from_global_id(image_id)
        post.main_image = Document._meta.model.objects.get(pk=gid)

    post.save(request=request)

    post.tags.clear()
    from tags.models import Tag
    tags_raw = args.get('tags', '')
    for tag_title in tags_raw.split(','):
        tag_title = tag_title.strip(' \t\n\r')
        tag_slug = slugify(tag_title)

        if len(tag_title) == 0:
            # don't save empty tag
            continue

        try:
            tag = Tag.objects.get(slug=tag_slug)
        except Tag.DoesNotExist:
            tag = Tag(
                title=tag_title,
                slug=tag_slug,
            )
            tag.save(request=request)
        post.tags.add(tag.document)

    return post


class PostCreate(Mutation):
    class Input:
        url = graphene.String(required=True)
        title = graphene.String(required=True)
        body = graphene.String(required=True)
        summary = graphene.String(required=False)
        published_at = DateTimeField(required=True)
        main_image = graphene.ID(required=False)
        tags = graphene.String()

    post = graphene.Field(Post)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        post = Post._meta.model()
        post = post_save(post, input, info.context)
        return PostCreate(post=post)


class PostEdit(Mutation):
    class Input:
        id = graphene.ID(required=True)
        url = graphene.String(required=True)
        title = graphene.String(required=True)
        body = graphene.String(required=True)
        summary = graphene.String(required=False)
        published_at = DateTimeField(required=True)
        main_image = graphene.ID(required=False)
        tags = graphene.String()

    post = graphene.Field(Post)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        post = Post._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, post, 'edit')
        if error:
            return error

        post = post_save(post, input, info.context)
        return PostEdit(post=post)


class PostDelete(Mutation):
    class Input:
        id = graphene.ID(required=True)

    postDeletedID = graphene.ID(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        gid_type, gid = from_global_id(input.get('id'))
        post = Post._meta.model.objects.get(document_id=gid)

        error = has_permission(cls, info.context, post, 'delete')
        if error:
            return error

        post.delete(request=info.context)

        return PostDelete(postDeletedID=input.get('id'))
