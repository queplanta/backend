import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField

from db.models import DocumentBase


class List(DocumentBase):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True)
    url = models.SlugField(max_length=255)
    items = JSONField(null=True)

    def add_item(self, document_id, notes):
        items = self.items
        if not items:
            items = []

        item = {
            'id': str(uuid.uuid1()),
            'item_id': document_id,
            'notes': notes
        }

        items.append(item)
        self.items = items

        return item
