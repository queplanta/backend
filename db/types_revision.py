import graphene
from graphene_django import DjangoConnectionField

from .models_graphql import Revision, Document
from .types import DocumentBase


class DocumentRevisionBase(DocumentBase, graphene.AbstractType):
    document = graphene.Field(Document)
    revision_current = graphene.Field(Revision)
    revision_created = graphene.Field(Revision)
    revisions = DjangoConnectionField(Revision)

    def resolve_document(self, args, context, info):
        if self.document_id:
            return Document._meta.model.objects.get(pk=self.document_id)

    def resolve_revision_current(self, args, context, info):
        if self.document.revision_tip_id:
            return Revision._meta.model.objects.get(
                pk=self.document.revision_tip_id)

    def resolve_revision_created(self, args, context, info):
        if self.document.revision_created_id:
            return Revision._meta.model.objects.get(
                pk=self.document.revision_created_id)

    def resolve_revisions(self, args, context, info):
        return Revision._meta.model.objects.filter(
            document_id=self.document_id).order_by('-created_at')
