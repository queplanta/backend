from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from ipware.ip import get_real_ip


class BigIntegerPK(models.Model):
    # id = models.BigIntegerField(primary_key=True)

    class Meta:
        abstract = True


class DocumentID(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)

    revisions_count = models.IntegerField(default=0)
    revision_tip_id = models.BigIntegerField(null=True, blank=True)
    revision_created_id = models.BigIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def get_object(self):
        return self.content_type.model_class().objects_revisions.get(
            pk=self.revision_tip_id)

    @property
    def revision_tip(self):
        return Revision.objects.get(pk=self.revision_tip_id)

    @property
    def revision_created(self):
        return Revision.objects.get(pk=self.revision_created_id)

REVISION_TYPES_CREATE = 'create'
REVISION_TYPES_CHANGE = 'change'
REVISION_TYPES_DELETE = 'delete'

REVISION_TYPES = (
    (REVISION_TYPES_CREATE, "Create"),
    (REVISION_TYPES_CHANGE, "Change"),
    (REVISION_TYPES_DELETE, "Delete"),
)


class Revision(models.Model):
    type = models.CharField(max_length=6, choices=REVISION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, on_delete=models.PROTECT)
    document = models.ForeignKey(DocumentID, on_delete=models.PROTECT)

    author = models.ForeignKey(DocumentID, related_name='authored_revisions',
                               null=True, on_delete=models.PROTECT)
    author_ip = models.GenericIPAddressField(null=True)
    author_useragent = models.CharField(max_length=512, null=True)
    message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def get_object(self):
        return self.document.content_type.model_class().objects_revisions.get(
            pk=self.pk)


class TipManager(models.Manager):
    def get_queryset(self):
        return super(TipManager, self).get_queryset().filter(
            is_tip=True, document__deleted_at__isnull=True)


class DocumentBase(models.Model):
    revision = models.OneToOneField(Revision, primary_key=True,
                                    on_delete=models.PROTECT)
    document = models.ForeignKey(DocumentID, on_delete=models.PROTECT)
    is_tip = models.NullBooleanField(null=True)

    # is_deleted field just to store a delete revision
    is_deleted = models.NullBooleanField(null=True)

    objects_revisions = models.Manager()
    objects = TipManager()

    class Meta:
        abstract = True
        unique_together = ('is_tip', 'document')

    @property
    def revisions(self):
        return self.__class__.objects_revisions.filter(document=self.document)

    def save(self, request, parent=None, message=None, **kwargs):
        if 'update_fields' in kwargs:
            # does not create a new revion if update_fields present
            return super(DocumentBase, self).save(**kwargs)

        if not self.document_id:
            self.document = DocumentID.objects.create(
                content_type=ContentType.objects.get_for_model(self)
            )

        parent_id = None
        if self.revision_id and not parent:
            parent_id = self.revision_id
        elif parent:
            parent_id = parent.pk

        author = None
        ip = None
        useragent = None
        if request:
            if request.user.is_authenticated():
                author = request.user
            ip = get_real_ip(request)
            useragent = request.META.get('HTTP_USER_AGENT')

        revision_type = None
        if not parent_id:
            revision_type = REVISION_TYPES_CREATE
        elif self.is_deleted:
            revision_type = REVISION_TYPES_DELETE
        else:
            revision_type = REVISION_TYPES_CHANGE

        revision = Revision.objects.create(
            type=revision_type,
            document=self.document,
            parent_id=parent_id,
            author=author.document if author else None,
            author_ip=ip,
            author_useragent=useragent,
            message=message,
        )

        self.revision = revision
        self.is_tip = True

        # set other revisions as not tip
        self.__class__.objects_revisions.filter(
            document=self.document).update(is_tip=None)

        if not self.document.revision_created_id:
            self.document.revision_created_id = revision.pk
        self.document.revision_tip_id = revision.pk
        self.document.revisions_count = models.F('revisions_count') + 1
        self.document.save(update_fields=['revision_tip_id',
                                          'revision_created_id',
                                          'revisions_count'])

        super(DocumentBase, self).save(**kwargs)

    def delete(self, request, **kwargs):
        self.document.deleted_at = timezone.now()
        self.document.save(update_fields=['deleted_at'])

        self.is_deleted = True
        self.save(request=request, **kwargs)
