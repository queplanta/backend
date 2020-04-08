from django.db import models
from django.contrib.contenttypes.models import ContentType

from db.models import DocumentBase, DocumentID
from utils.upload import set_upload_to_random_filename


class Image(DocumentBase):
    parent = models.ForeignKey(DocumentID, related_name="images", on_delete=models.DO_NOTHING, null=True)
    image = models.ImageField(
        max_length=512,
        upload_to=set_upload_to_random_filename('images')
    )
    description = models.TextField(null=True, blank=True)

    REPUTATION_VALUE = 1
