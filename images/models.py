from django.db import models

from db.models import DocumentBase
from utils.upload import set_upload_to_random_filename


class Image(DocumentBase):
    image = models.ImageField(
        max_length=512,
        upload_to=set_upload_to_random_filename('images')
    )
    description = models.TextField(null=True, blank=True)

    REPUTATION_VALUE = 1
