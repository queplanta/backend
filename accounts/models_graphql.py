import graphene
from graphene.utils import with_context
from graphene.contrib.django import DjangoNode

from db.types import DocumentBase

from .models import User as UserModel


class User(DocumentBase, DjangoNode):
    is_authenticated = graphene.Boolean()

    @with_context
    def resolve_is_authenticated(self, args, request, info):
        return request.user.is_authenticated()

    class Meta:
        model = UserModel
        exclude_fields = ('is_superuser', 'password', 'email', 'is_staff')
