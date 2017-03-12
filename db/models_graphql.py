import graphene
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene.relay import Node

from accounts.models_graphql import User

from .models import (
    Revision as RevisionModel,
    DocumentID as DocumentIDModel
)


def get_document_type():
    from db.models_graphql import Document
    return Document


class Revision(DjangoObjectType):
    id_int = graphene.Int()
    author = graphene.Field(User)
    after = DjangoConnectionField(lambda: Revision)
    before = graphene.Field(lambda: Revision)
    document = graphene.Field(get_document_type)
    object = graphene.Field(Node)
    type = graphene.String()
    is_tip = graphene.Boolean()

    class Meta:
        model = RevisionModel
        interfaces = (Node, )

    def resolve_id_int(self, args, request, info):
        return self.id

    def resolve_author(self, args, context, info):
        if self.author_id:
            return User._meta.model.objects.get(document_id=self.author_id)

    def resolve_after(self, args, context, info):
        return Revision._meta.model.objects.filter(
            parent_id=self.id
        ).order_by('-created_at')

    def resolve_before(self, args, context, info):
        return self.parent

    def resolve_object(self, args, context, info):
        Model = self.document.content_type.model_class()
        return Model.objects_revisions.get(pk=self.pk)

    def resolve_is_tip(self, args, context, info):
        return self.id == self.document.revision_tip_id


class Document(DjangoObjectType):
    revision_tip = graphene.Field(Revision)
    revision_created = graphene.Field(Revision)
    owner = graphene.Field(User)

    class Meta:
        model = DocumentIDModel
        interfaces = (Node, )

    def resolve_revision_tip(self, args, context, info):
        if self.revision_tip_id:
            return Revision._meta.model.objects.get(pk=self.revision_tip_id)

    def resolve_revision_created(self, args, context, info):
        if self.revision_created_id:
            return Revision._meta.model.objects.get(
                pk=self.revision_created_id
            )

    def resolve_owner(self, args, context, info):
        if self.owner_id:
            return User._meta.model.objects.get(document_id=self.owner_id)
