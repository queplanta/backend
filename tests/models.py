from django.db import models

from db.models import DocumentBase
from db.fields import ManyToManyField


class Tag(DocumentBase):
	title = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255)
	class Meta:
		unique_together = ("is_tip", "slug")

	@property
	def pages(self):
		return Page.objects.filter(tags=self)


class PageTag(models.Model):
	page = models.ForeignKey('Page', to_field='revision_id', on_delete=models.CASCADE)
	tag = models.ForeignKey(Tag, to_field='document_id', on_delete=models.CASCADE)


class Page(DocumentBase):
	title = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255)
	tags = ManyToManyField(Tag, through=PageTag)

	class Meta:
		unique_together = ("is_tip", "slug")
	# with migrations set unique_together using partial indexes
	# so we can have multiple is_tip = False values and just
	# one with is_tip = True
	
	def __str__(self):
		return str(self.revision_id, ": ", self.title) if self.revision_id else self.title
