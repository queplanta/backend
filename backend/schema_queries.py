import graphene
from graphene import relay
from graphene.utils import with_context
from graphene.contrib.django.filter import DjangoFilterConnectionField
from graphene.contrib.django.debug import DjangoDebug

from accounts.models_graphql import User
from posts.models_graphql import Post
from tags.models_graphql import Tag
from voting.models_graphql import Vote
from commenting.models_graphql import Comment
from db.models_graphql import Revision, Document

from .fields import GetBy, GetByRevisionID


def get_default_viewer(args, context, info):
    return Query(id='viewer')


class NodeField(relay.NodeField):
    @with_context
    def resolver(self, instance, args, context, info):
        obj = super(NodeField, self).resolver(instance, args, context, info)

        global_id = args.get('id')
        from graphql_relay.node.node import from_global_id
        schema = info.schema.graphene_schema
        try:
            _type, _id = from_global_id(global_id)
        except:
            return None
        object_type = schema.get_type(_type)

        return object_type(obj)


class Query(graphene.ObjectType):
    id = graphene.ID()
    viewer = graphene.Field('self')
    me = graphene.Field(User)
    user = relay.NodeField(User)
    user_by_username = GetBy(User, username=graphene.String().NonNull)

    revision = relay.NodeField(Revision)
    document = relay.NodeField(Document)

    all_posts = DjangoFilterConnectionField(Post, on='objects')
    post = relay.NodeField(Post)
    post_by_url = GetBy(Post, url=graphene.String().NonNull)
    post_by_revision_id = GetByRevisionID(Post, id=graphene.ID().NonNull)

    all_tags = DjangoFilterConnectionField(Tag)
    tag = relay.NodeField(Tag)
    tag_by_slug = GetBy(Tag, slug=graphene.String().NonNull)
    tag_by_revision_id = GetByRevisionID(Tag, id=graphene.ID().NonNull)

    all_comments = DjangoFilterConnectionField(Tag)
    comment = relay.NodeField(Comment)
    comment_by_parent_id = GetBy(Comment, id=graphene.ID().NonNull)

    vote = relay.NodeField(Vote)

    node = NodeField()

    debug = graphene.Field(DjangoDebug, name='__debug')

    @with_context
    def resolve_viewer(self, *args, **kwargs):
        return get_default_viewer(*args, **kwargs)

    @with_context
    def resolve_me(self, args, request, info):
        if request.user.is_authenticated():
            return request.user
        return None
