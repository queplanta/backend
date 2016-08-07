from django.test import TestCase

from tests.models import Page, Tag, PageTag


class RevisionsTest(TestCase):
	def test_create_page(self):
		tag_1 = Tag.objects.create(title='Tag 1', slug="tag-1")
		created_page = Page(title="Example", slug="example")
		created_page.save()
		PageTag.objects.create(page=created_page, tag=tag_1)
		
		tag_2 = Tag.objects.create(title='Tag 2', slug="tag-2")
		updated_page = Page.objects.get(slug=created_page.slug)
		updated_page.title = "Title updated"
		updated_page.save()
		PageTag.objects.create(page=updated_page, tag=tag_1)
		PageTag.objects.create(page=updated_page, tag=tag_2)

		# must have 2 page revisions:
		page_revisions = created_page.revisions.all()
		self.assertEqual(2, page_revisions.count())

		# just 1 page on the database
		self.assertEqual(1, Page.objects.all().count())

		# updated page must be the tip page
		retrived_page = Page.objects.get(slug=created_page.slug)
		self.assertEqual(retrived_page, updated_page)

		# compare m2m relationships
		self.assertEqual(1, created_page.tags.count())
		self.assertEqual(created_page.tags.first(), tag_1)
		self.assertEqual(2, updated_page.tags.count())
		self.assertEqual(updated_page.tags.first(), tag_1)
		self.assertEqual(updated_page.tags.last(), tag_2)
		self.assertEqual(1, tag_1.pages.count())
		self.assertEqual(tag_1.pages.first(), updated_page)

		# compare db versions with local variable versions
		self.assertEqual([created_page, updated_page], list(page_revisions))
		self.assertEqual(updated_page.document.revision_created_id, created_page.revision_id)
		self.assertEqual(updated_page.document.revision_tip_id, updated_page.revision_id)

		updated_page.delete()
		self.assertEqual(0, Page.objects.all().count())
		self.assertEqual(0, tag_1.pages.count())
