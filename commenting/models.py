from django.db import models
from db.models import DocumentBase, DocumentID


class Comment(DocumentBase):
    parent = models.ForeignKey(DocumentID, related_name="comments", on_delete=models.CASCADE)
    body = models.TextField()

    REPUTATION_VALUE = 1

    def save(self, *args, **kwargs):
        super(Comment, self).save(*args, **kwargs)
        update_count(self)

    def delete(self, *args, **kwargs):
        super(Comment, self).delete(*args, **kwargs)
        update_count(self)


def update_count(comment):
    stats, created = CommentStats.objects.get_or_create(
        document=comment.parent
    )
    stats.count = Comment.objects.filter(
        parent=stats.document
    ).count()
    stats.save()


class CommentStats(models.Model):
    document = models.OneToOneField(DocumentID, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
