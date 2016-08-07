import graphene
from graphene.utils import with_context
from graphene.contrib.django import DjangoConnectionField

from .models_graphql import Revision, Document
from .types import DocumentBase


class DocumentRevisionBase(DocumentBase):
    document = graphene.Field(Document)
    revision_current = graphene.Field(Revision)
    revision_created = graphene.Field(Revision)
    revisions = DjangoConnectionField(Revision)

    def resolve_document(self, args, info):
        if self.document_id:
            return Document._meta.model.objects.get(pk=self.document_id)

    def resolve_revision_current(self, args, info):
        if self.document.revision_tip_id:
            return Revision._meta.model.objects.get(pk=self.document.revision_tip_id)

    def resolve_revision_created(self, args, info):
        if self.document.revision_created_id:
            return Revision._meta.model.objects.get(pk=self.document.revision_created_id)

    def resolve_revisions(self, args, info):
        return Revision._meta.model.objects.filter(document_id=self.document_id).order_by('-created_at')
