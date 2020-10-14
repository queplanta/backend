import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField

from db.models import DocumentBase, DocumentID


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


class CollectionItem(DocumentBase):
    plant = models.ForeignKey(
        DocumentID, related_name="collection_item_plant",
        blank=True, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(DocumentID, related_name="collection_item_user", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(WishItem, self).save(*args, **kwargs)
        update_count(self)

    def delete(self, *args, **kwargs):
        super(WishItem, self).delete(*args, **kwargs)
        update_count(self)


class WishItem(DocumentBase):
    plant = models.ForeignKey(
        DocumentID, related_name="wish_item_plant",
        blank=True, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(DocumentID, related_name="wish_item_user", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(WishItem, self).save(*args, **kwargs)
        update_count(self)

    def delete(self, *args, **kwargs):
        super(WishItem, self).delete(*args, **kwargs)
        update_count(self)


def update_count(user):
    stats, created = ListStats.objects.get_or_create(
        document=user.document
    )
    stats.collection_count = CollectionItem.objects.filter(user=user.document).count()
    stats.wish_count = WishItem.objects.filter(user=user.document).count()
    stats.save()


class ListStats(models.Model):
    document = models.OneToOneField(DocumentID, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    collection_count = models.IntegerField(default=0)
    wish_count = models.IntegerField(default=0)