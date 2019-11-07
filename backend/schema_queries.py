import os
import graphene
from graphene import relay
from graphene.relay.node import NodeField as RelayNodeField
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.debug import DjangoDebug

from django.db.models import Q

from accounts.models_graphql import Query as UserQuery
from posts.models_graphql import Post
from pages.models_graphql import Page
from tags.models_graphql import Tag
from voting.models_graphql import Vote
from commenting.models_graphql import Comment
from life.models_graphql import (
    LifeNode, Quizz, generate_quiz, CommonName
)
from occurrences.models_graphql import Occurrence, OccurrenceFilter, SuggestionID
from db.models_graphql import Revision, Document
from lists.models_graphql import List
from images.models_graphql import Image
from shortenr.models_graphql import Query as ShortnerQuery

from .fields import GetBy


def get_default_viewer(*args, **kwargs):
    return Query(id='viewer')


class NodeField(RelayNodeField):
    def get_resolver(self, parent_resolver):
        resolver = super().get_resolver(parent_resolver)

        def get_node(instance, info, **kwargs):
            global_id = kwargs.get('id')
            if global_id == 'viewer':
                return get_default_viewer(instance, info, **kwargs)
            return resolver(instance, info, **kwargs)

        return get_node


class Query(UserQuery, ShortnerQuery, graphene.ObjectType):
    id = graphene.ID(required=True)
    viewer = graphene.Field(lambda: Query)

    revision = relay.Node.Field(Revision)
    document = relay.Node.Field(Document)

    all_posts = DjangoFilterConnectionField(Post, on='objects')
    post = relay.Node.Field(Post)
    post_by_url = GetBy(Post, url=graphene.String(required=True))

    all_pages = DjangoFilterConnectionField(Page, on='objects')
    page = relay.Node.Field(Page)
    page_by_url = GetBy(Page, url=graphene.String(required=True))

    all_tags = DjangoFilterConnectionField(Tag)
    tag = relay.Node.Field(Tag)
    tag_by_slug = GetBy(Tag, slug=graphene.String(required=True))

    all_comments = DjangoFilterConnectionField(Comment)
    comment = relay.Node.Field(Comment)
    comment_by_parent_id = GetBy(Comment, id=graphene.ID(required=True))

    image = relay.Node.Field(Image)

    vote = relay.Node.Field(Vote)

    lifeNode = relay.Node.Field(LifeNode)
    lifeNodeByIntID = GetBy(LifeNode, document_id=graphene.Int(required=True))
    allLifeNode = DjangoFilterConnectionField(LifeNode, args={
        'search': graphene.Argument(graphene.String, required=False),
        'edibles': graphene.Argument(graphene.Boolean, required=False)
    }, total_found2=graphene.Int(required=False, name='totalFound2'))

    occurrence = relay.Node.Field(Occurrence)
    allOccurrences = DjangoFilterConnectionField(Occurrence, filterset_class=OccurrenceFilter)
    allWhatIsThis = DjangoFilterConnectionField(Occurrence, filterset_class=OccurrenceFilter)
    suggestionID = relay.Node.Field(SuggestionID)

    list = relay.Node.Field(List)

    lifeNodeQuizz = graphene.Field(Quizz, resolver=generate_quiz)

    node = NodeField(relay.Node)

    version = graphene.String()

    debug = graphene.Field(DjangoDebug, name='_debug')

    class Meta:
        interfaces = (relay.Node,)

    def resolve_viewer(self, *args, **kwargs):
        return get_default_viewer(*args, **kwargs)

    def resolve_allOccurrences(self, info, **kwargs):
        qs = Occurrence._meta.model.objects.all()
        return qs.order_by('-document__created_at').filter(
            location__isnull=False, identity__isnull=False)

    def resolve_allWhatIsThis(self, info, **kwargs):
        qs = Occurrence._meta.model.objects.all()
        return qs.order_by('-document__created_at').filter(is_request=True)

    def resolve_allLifeNode(self, info, **args):
        qs = LifeNode._meta.model.objects.all()
        if 'edibles' in args and bool(args['edibles']):
            qs = qs.filter(edibility__gte=1)
        if 'search' in args and len(args['search']) > 2:
            s = args['search'].strip()
            q_objects = Q(title__icontains=s)

            commonNames = CommonName._meta.model.objects.filter(
                name__icontains=s
            ).distinct().values_list('document_id', flat=True)

            if len(commonNames) > 0:
                q_objects |= Q(commonNames__id__in=commonNames)

            qs = qs.filter(q_objects)
            return qs.distinct()

        return qs.order_by('document_id').distinct()

    def resolve_version(self, info):
        return os.getenv('VERSION', 'master')
