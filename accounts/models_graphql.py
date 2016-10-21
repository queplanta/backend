from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType, DjangoConnectionField

from sorl.thumbnail import get_thumbnail

from db.types import DocumentBase

from .models import User as UserModel


class Image(graphene.ObjectType):
    x140x140 = graphene.String()
    original = graphene.String()

    def __init__(self, f, *args, **kwargs):
        self._file = f
        return super(Image, self).__init__(*args, **kwargs)

    def resolve_original(self, args, request, info):
        return self._file.url

    def resolve_x140x140(self, args, request, info):
        return get_thumbnail(self._file, '140x140', crop='center',
                             quality=90).url


def get_revision_type():
    from db.models_graphql import Revision
    return Revision


class User(DocumentBase, DjangoObjectType):
    is_authenticated = graphene.Boolean()
    avatar = graphene.Field(Image)

    actions = DjangoConnectionField(get_revision_type)

    def resolve_is_authenticated(self, args, request, info):
        return request.user.is_authenticated()

    class Meta:
        model = UserModel
        exclude_fields = ('is_superuser', 'password', 'is_staff')
        interfaces = (Node, )

    def resolve_email(self, args, request, info):
        if request.user.is_authenticated() and\
            (self.document == request.user.document or
                request.user.is_superuser):
            return self.email
        return _("Você não tem permissão")

    def resolve_avatar(self, args, request, info):
        if not self.avatar:
            self.avatar.name = settings.DEFAULT_USER_AVATAR
        return Image(self.avatar)

    def resolve_actions(self, args, request, info):
        Revision = get_revision_type()
        import time
        time.sleep(3)
        return Revision._meta.model.objects.filter(
            author_id=self.document.pk).order_by('-created_at')
