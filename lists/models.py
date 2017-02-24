from django.db import models
from django.contrib.postgres.fields import JSONField

from db.models import DocumentBase


class List(DocumentBase):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True)
    url = models.SlugField(max_length=255)
    items = JSONField(null=True)
