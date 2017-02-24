import graphene
from .choices import (
    PRIVACY_CHOICES,
    PRIVACY_PRIVATE, PRIVACY_FRIENDS, PRIVACY_PUBLIC
)


class Privacy(graphene.Enum):
    PRIVATE = PRIVACY_PRIVATE
    FRIENDS = PRIVACY_FRIENDS
    PUBLIC = PRIVACY_PUBLIC

    @property
    def description(self):
        return dict(PRIVACY_CHOICES)[self._value_]
