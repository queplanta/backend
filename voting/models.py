from django.db import models

from db.models import DocumentBase, DocumentID
from .ranking import confidence, hot


class Vote(DocumentBase):
    value = models.IntegerField(default=0)
    parent = models.ForeignKey(DocumentID, related_name="votes")
    author = models.ForeignKey(DocumentID, related_name="votes_author")

    # class Meta:
    #   unique_together = ('object_id', 'content_type', 'user')
    # before using it, it should be an partial index with is_tip = True

    def save(self, *args, **kwargs):
        super(Vote, self).save(*args, **kwargs)
        update_num_votes(self)

    def delete(self, *args, **kwargs):
        super(Vote, self).delete(*args, **kwargs)
        update_num_votes(self)


def update_num_votes(vote):
    stats, created = VoteStats.objects.get_or_create(
        document=vote.parent
    )

    votes = Vote.objects.filter(parent=stats.document)

    stats.count = votes.count()

    stats.sum_values = votes.aggregate(total=models.Sum('value'))['total']
    if not stats.sum_values:
        stats.sum_values = 0

    stats.count_ups = votes.filter(
        value__gte=1).count()
    stats.count_downs = votes.filter(
        value__lte=-1).count()

    stats.confidence_score = confidence(ups=stats.count_ups + 1,
                                        downs=stats.count_downs)
    stats.hot_score = hot(
        ups=stats.count_ups + 1,
        downs=stats.count_downs,
        date=stats.document.revision_created.created_at
    )
    stats.save()


class VoteStats(models.Model):
    document = models.OneToOneField(DocumentID)
    count = models.IntegerField(default=0)
    sum_values = models.IntegerField(default=0)
    count_downs = models.IntegerField(default=0)
    count_ups = models.IntegerField(default=0)
    confidence_score = models.FloatField(default=0.0, editable=False)
    hot_score = models.FloatField(default=0.0, editable=False)
