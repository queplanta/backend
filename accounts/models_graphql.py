from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType, DjangoConnectionField

from db.types import DocumentBase
from images.fields import Thumbnail

from .models import User as UserModel


def get_revision_type():
    from db.models_graphql import Revision
    return Revision


class User(DocumentBase, DjangoObjectType):
    is_authenticated = graphene.Boolean()
    avatar = Thumbnail()

    actions = DjangoConnectionField(get_revision_type)

    def resolve_is_authenticated(self, info):
        return info.context.user.is_authenticated

    class Meta:
        model = UserModel
        exclude_fields = ('is_superuser', 'password', 'is_staff')
        interfaces = (Node, )

    def resolve_email(self, info):
        if info.context.user.is_authenticated and\
            (self.document == info.context.user.document or
                info.context.user.is_superuser):
            return self.email
        return _("Você não tem permissão")

    def resolve_avatar(self, info):
        if not self.avatar:
            self.avatar.name = settings.DEFAULT_USER_AVATAR
        return self.avatar

    def resolve_actions(self, info):
        Revision = get_revision_type()
        return Revision._meta.model.objects.filter(
            author_id=self.document.pk).order_by('-created_at')
