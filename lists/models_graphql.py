import graphene
from graphene_django import DjangoObjectType
from graphene.relay import Node

from db.models import DocumentID
from db.types_revision import DocumentNode, DocumentBase
from db.graphene import CountedConnection

from .models import List as ListModel, CollectionItem as CollectionItemModel, WishItem as WishItemModel
from commenting.models_graphql import CommentsNode
from voting.models_graphql import VotesNode
from life.models_graphql import LifeNode


class List(DjangoObjectType, DocumentBase):
    items = graphene.List(lambda: ListItem)

    class Meta:
        model = ListModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)
        connection_class = CountedConnection

    def resolve_items(self, info):
        if not self.items:
            return []

        items = []
        for item in self.items:
            items.append(ListItem(
                id=item['id'],
                item=DocumentID.objects.get(id=item['item_id']).get_object(),
                notes=item['notes']
            ))
        return items


class ListItem(graphene.ObjectType):
    id = graphene.String()
    item = graphene.Field(Node)
    notes = graphene.String(required=False)


class CollectionItem(DjangoObjectType, DocumentBase):
    plant = graphene.Field(LifeNode)

    class Meta:
        model = CollectionItemModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)
        connection_class = CountedConnection

    def resolve_plant(self, info):
        if not self.plant_id:
            return None
        return LifeNode._meta.model.objects.get(document_id=self.plant_id)


class WishItem(DjangoObjectType, DocumentBase):
    plant = graphene.Field(LifeNode)

    class Meta:
        model = WishItemModel
        interfaces = (Node, DocumentNode, CommentsNode, VotesNode)
        connection_class = CountedConnection

    def resolve_plant(self, info):
        if not self.plant_id:
            return None
        return LifeNode._meta.model.objects.get(document_id=self.plant_id)
