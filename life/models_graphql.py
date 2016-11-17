import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType, DjangoConnectionField

from db.types_revision import DocumentRevisionBase

from .models import (
    LifeNode as LifeNodeModel,
    CommonName as CommonNameModel,
    Characteristic as CharacteristicModel,
    RANK_STRING_BY_INT
)
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode
from images.models_graphql import Image
from tags.models_graphql import Tag


class LifeNode(DocumentRevisionBase, CommentsNode, VotesNode,
               DjangoObjectType):
    parent = graphene.Field(lambda: LifeNode)
    parents = graphene.List(lambda: LifeNode)
    rank = graphene.String()
    rankDisplay = graphene.String()
    commonNames = graphene.List(graphene.String)

    children = DjangoConnectionField(lambda: LifeNode)
    images = DjangoConnectionField(lambda: Image)
    characteristics = DjangoConnectionField(lambda: Characteristic)

    class Meta:
        model = LifeNodeModel
        interfaces = (Node,)

    def resolve_parent(self, args, request, info):
        if self.parent:
            return self.parent.get_object()

    def resolve_parents(self, args, request, info):
        def get_parents(obj):
            parents = []
            if obj.parent:
                parent = obj.parent.get_object()
                parents.append(parent)
                parents.extend(get_parents(parent))
            return parents
        return get_parents(self)

    def resolve_rank(self, args, request, info):
        return RANK_STRING_BY_INT[self.rank]

    def resolve_rankDisplay(self, args, request, info):
        return self.get_rank_display()

    def resolve_commonNames(self, args, request, info):
        return CommonNameModel._meta.model.objects.filter(
            document__lifeNode_commonName=self
        ).order_by('name').values_list('name', flat=True)

    def resolve_children(self, args, request, info):
        return LifeNode._meta.model.objects.filter(
            parent=self.document
        ).order_by('title')

    def resolve_images(self, args, context, info):
        return Image._meta.model.objects.filter(
            document__lifeNode_image=self)

    def resolve_characteristics(self, args, request, info):
        return Characteristic._meta.model.objects.filter(
            lifeNode=self.document
        )


class Characteristic(DocumentRevisionBase, CommentsNode, VotesNode,
                     DjangoObjectType):
    tag = graphene.Field(lambda: Tag)
    title = graphene.String()

    class Meta:
        model = CharacteristicModel
        interfaces = (Node,)

    def resolve_tag(self, args, request, info):
        return self._get_tag()

    def resolve_title(self, args, request, info):
        return self._get_tag().title
