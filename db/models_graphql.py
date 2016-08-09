import graphene
from graphene.contrib.django import DjangoNode, DjangoConnectionField

from accounts.models_graphql import User

from .models import (
    Revision as RevisionModel,
    DocumentID as DocumentIDModel
)


class Revision(DjangoNode):
    author = graphene.Field(User)
    after = DjangoConnectionField('self')
    before = graphene.Field('self')

    class Meta:
        model = RevisionModel

    def resolve_author(self, args, info):
        if self.author_id:
            return User._meta.model.objects.get(document_id=self.author_id)

    def resolve_after(self, args, info):
        return Revision._meta.model.objects.filter(
            parent_id=self.id
        ).order_by('-created_at')

    def resolve_before(self, args, info):
        return self.parent


class Document(DjangoNode):
    revision_tip = graphene.Field(Revision)
    revision_created = graphene.Field(Revision)

    class Meta:
        model = DocumentIDModel

    def resolve_revision_tip(self, args, info):
        if self.revision_tip_id:
            return Revision._meta.model.objects.get(pk=self.revision_tip_id)

    def resolve_revision_created(self, args, info):
        if self.revision_created_id:
            return Revision._meta.model.objects.get(
                pk=self.revision_created_id
            )
