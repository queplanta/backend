import django_filters

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField

from db.types import DocumentBase
from db.graphene import CountedConnection

from images.fields import Thumbnail
from backend.fields import GetBy

from .models import User as UserModel


def get_revision_type():
    from db.models_graphql import Revision
    return Revision


def get_collection_item_type():
    from lists.models_graphql import CollectionItem
    return CollectionItem


def get_wish_item_type():
    from lists.models_graphql import WishItem
    return WishItem


def get_occurrence_type():
    from occurrences.models_graphql import Occurrence
    return Occurrence


class User(DjangoObjectType, DocumentBase):
    is_authenticated = graphene.Boolean()
    avatar = Thumbnail()

    actions = DjangoConnectionField(get_revision_type)

    collection_list = DjangoConnectionField(get_collection_item_type)
    wish_list = DjangoConnectionField(get_wish_item_type)
    occurrence_list = DjangoConnectionField(get_occurrence_type)

    my_perms = graphene.List(graphene.String)

    class Meta:
        model = UserModel
        exclude_fields = ('is_superuser', 'password', 'is_staff')
        interfaces = (Node, )
        connection_class = CountedConnection

    @classmethod
    def get_node(cls, info, id):
        return cls._meta.model.objects.get(document_id=id)

    def resolve_is_authenticated(self, info):
        return info.context.user.is_authenticated

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

    def resolve_collection_list(self, info, **kwargs):
        CollectionItem = get_collection_item_type()
        return CollectionItem._meta.model.objects.filter(
            user_id=self.document_id
        ).order_by('-document__created_at')

    def resolve_wish_list(self, info, **kwargs):
        WishItem = get_wish_item_type()
        return WishItem._meta.model.objects.filter(
            user_id=self.document_id
        ).order_by('-document__created_at')

    def resolve_occurrences_list(self, info, **kwargs):
        qs = Occurrence._meta.model.objects.filter(author=self.document)
        return qs.order_by('-document__created_at').filter(
            location__isnull=False,
            identity__isnull=False,
            identity__deleted_at__isnull=True
        )

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
            ('document__liststats__collection_count', 'collection_count'),
            ('document__liststats__wish_count', 'wish_count'),
        )
    )

    class Meta:
        model = UserModel
        fields = ['name_startswith', 'order_by']


    @property
    def qs(self):
        qs = super().qs
        order_by = self.data.get('order_by')
        if 'collection_count' in order_by and 'collection_count' in order_by:
            qs = qs.filter(document__liststats__isnull=False)
        return qs


class Query(object):
    me = graphene.Field(User)
    user = Node.Field(User)
    user_by_username = GetBy(User, username=graphene.String(required=True))
    all_users = DjangoFilterConnectionField(User, filterset_class=UserFilter)

    def resolve_me(parent, info):
        if info.context.user.is_authenticated:
            return UserModel.objects.get(pk=info.context.user.pk)
        return None

