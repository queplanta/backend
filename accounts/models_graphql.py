import django_filters

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField

from db.types import DocumentBase
from images.fields import Thumbnail
from backend.fields import GetBy

from .models import User as UserModel


def get_revision_type():
    from db.models_graphql import Revision
    return Revision


class User(DjangoObjectType, DocumentBase):
    is_authenticated = graphene.Boolean()
    avatar = Thumbnail()

    actions = DjangoConnectionField(get_revision_type)

    my_perms = graphene.List(graphene.String)

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

    def resolve_avatar(self, info, **kwargs):
        if not self.avatar:
            self.avatar.name = settings.DEFAULT_USER_AVATAR
        return self.avatar

    def resolve_actions(self, info, **kwargs):
        Revision = get_revision_type()
        return Revision._meta.model.objects.filter(
            author_id=self.document.pk).order_by('-created_at')

    def resolve_my_perms(self, info, **kwargs):
        if self.is_superuser:
            return ['add_page', 'add_post']
        return []


class UserFilter(django_filters.FilterSet):
    name_startswith = django_filters.CharFilter(field_name='first_name', lookup_expr='istartswith')

    order_by = django_filters.OrderingFilter(
        fields=(
            ('reputation', 'reputation'),
            ('date_joined', 'date_joined'),
        )
    )

    class Meta:
        model = UserModel
        fields = ['name_startswith', 'order_by']


class Query(object):
    me = graphene.Field(User)
    user = Node.Field(User)
    user_by_username = GetBy(User, username=graphene.String(required=True))
    all_users = DjangoFilterConnectionField(User, filterset_class=UserFilter)

    def resolve_me(parent, info):
        if info.context.user.is_authenticated:
            return UserModel.objects.get(pk=info.context.user.pk)
        return None

