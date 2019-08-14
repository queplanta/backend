import graphene
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene.relay import Node

from accounts.models_graphql import User

from .models import (
    Revision as RevisionModel,
    DocumentID as DocumentIDModel,
    REVISION_TYPES, REVISION_TYPES_CREATE,
    REVISION_TYPES_CHANGE, REVISION_TYPES_DELETE
)


def get_document_type():
    from db.models_graphql import Document
    return Document


class RevisionType(graphene.Enum):
    CREATE = REVISION_TYPES_CREATE
    UPDATE = REVISION_TYPES_CHANGE
    DELETE = REVISION_TYPES_DELETE

    @property
    def description(self):
        return dict(REVISION_TYPES)[self._value_]


class Revision(DjangoObjectType):
    id_int = graphene.Int()
    author = graphene.Field(User)
    after = DjangoConnectionField(lambda: Revision)
    before = graphene.Field(lambda: Revision)
    document = graphene.Field(get_document_type)
    object = graphene.Field(Node)
    type = graphene.Field(RevisionType)
    typeDisplay = graphene.String()
    is_tip = graphene.Boolean()

    class Meta:
        model = RevisionModel
        interfaces = (Node, )

    def resolve_id_int(self, info):
        return self.id

    def resolve_author(self, info):
        if self.author_id:
            return User._meta.model.objects.get(document_id=self.author_id)

    def resolve_after(self, info):
        return Revision._meta.model.objects.filter(
            parent_id=self.id
        ).order_by('-created_at')

    def resolve_before(self, info):
        return self.parent

    def resolve_object(self, info):
        Model = self.document.content_type.model_class()
        return Model.objects_revisions.get(pk=self.pk)

    def resolve_typeDisplay(self, info):
        return self.get_type_display()

    def resolve_is_tip(self, info):
        return self.id == self.document.revision_tip_id


class Document(DjangoObjectType):
    revision_tip = graphene.Field(Revision)
    revision_created = graphene.Field(Revision)
    owner = graphene.Field(User)

    class Meta:
        model = DocumentIDModel
        interfaces = (Node, )

    def resolve_revision_tip(self, info):
        if self.revision_tip_id:
            return Revision._meta.model.objects.get(pk=self.revision_tip_id)

    def resolve_revision_created(self, info):
        if self.revision_created_id:
            return Revision._meta.model.objects.get(
                pk=self.revision_created_id
            )

    def resolve_owner(self, info):
        if self.owner_id:
            return User._meta.model.objects.get(document_id=self.owner_id)
