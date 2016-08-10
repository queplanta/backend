from django.utils.translation import ugettext_lazy as _

import graphene
from graphene.utils import with_context
from graphene.contrib.django import DjangoNode

from sorl.thumbnail import get_thumbnail

from db.types import DocumentBase

from .models import User as UserModel


class Image(graphene.ObjectType):
    x140x140 = graphene.String()
    original = graphene.String()

    def __init__(self, f, *args, **kwargs):
        self._file = f
        return super(Image, self).__init__(*args, **kwargs)

    @with_context
    def resolve_original(self, args, request, info):
        return self._file.url

    @with_context
    def resolve_x140x140(self, args, request, info):
        return get_thumbnail(self._file, '140x140', crop='center',
                             quality=90).url


class User(DocumentBase, DjangoNode):
    is_authenticated = graphene.Boolean()
    avatar = graphene.Field(Image)

    @with_context
    def resolve_is_authenticated(self, args, request, info):
        return request.user.is_authenticated()

    class Meta:
        model = UserModel
        exclude_fields = ('is_superuser', 'password', 'is_staff')

    @with_context
    def resolve_email(self, args, request, info):
        if request.user.is_authenticated() and\
            (self.document == request.user.document or
                request.user.is_superuser):
            return self.email
        return _("Você não tem permissão")

    @with_context
    def resolve_avatar(self, args, request, info):
        if self.avatar:
            return Image(self.avatar)
        return None
