import graphene
from graphene import relay
from graphene.relay.node import NodeField as RelayNodeField
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.debug import DjangoDebug

from accounts.models_graphql import User
from posts.models_graphql import Post
from tags.models_graphql import Tag
from voting.models_graphql import Vote
from commenting.models_graphql import Comment
from life.models_graphql import LifeNode
from what.models_graphql import WhatIsThis, SuggestionID
from db.models_graphql import Revision, Document

from .fields import GetBy


def get_default_viewer(*args, **kwargs):
    return Query(id='viewer')


class NodeField(RelayNodeField):
    def get_resolver(self, parent_resolver):
        resolver = self.resolver or parent_resolver

        def get_node(instance, args, context, info):
            global_id = args.get('id')
            if global_id == 'viewer':
                return get_default_viewer(instance, args, context, info)
            return resolver(instance, args, context, info)

        return get_node


class Query(graphene.ObjectType):
    id = graphene.ID(required=True)
    viewer = graphene.Field(lambda: Query)
    me = graphene.Field(User)
    user = relay.Node.Field(User)
    user_by_username = GetBy(User, username=graphene.String(required=True))

    revision = relay.Node.Field(Revision)
    document = relay.Node.Field(Document)

    all_posts = DjangoFilterConnectionField(Post, on='objects')
    post = relay.Node.Field(Post)
    post_by_url = GetBy(Post, url=graphene.String(required=True))

    all_tags = DjangoFilterConnectionField(Tag)
    tag = relay.Node.Field(Tag)
    tag_by_slug = GetBy(Tag, slug=graphene.String(required=True))

    all_comments = DjangoFilterConnectionField(Tag)
    comment = relay.Node.Field(Comment)
    comment_by_parent_id = GetBy(Comment, id=graphene.ID(required=True))

    vote = relay.Node.Field(Vote)

    lifeNode = relay.Node.Field(LifeNode)
    lifeNodeByIntID = GetBy(LifeNode, document_id=graphene.Int(required=True))
    allLifeNode = DjangoFilterConnectionField(LifeNode, args={
        'search': graphene.Argument(graphene.String, required=False)
    })

    whatIsThis = relay.Node.Field(WhatIsThis)
    allWhatIsThis = DjangoFilterConnectionField(WhatIsThis)
    suggestionID = relay.Node.Field(SuggestionID)

    node = NodeField(relay.Node)

    debug = graphene.Field(DjangoDebug, name='__debug')

    class Meta:
        interfaces = (relay.Node,)

    def resolve_viewer(self, *args, **kwargs):
        return get_default_viewer(*args, **kwargs)

    def resolve_me(self, args, request, info):
        if request.user.is_authenticated():
            return User._meta.model.objects.get(pk=request.user.pk)
        return None

    def resolve_allLifeNode(self, args, request, info):
        qs = LifeNode._meta.model.objects.all()
        if 'search' in args and len(args['search']) > 2:
            qs = qs.filter(title__icontains=args['search'])
        return qs
