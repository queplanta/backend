from django.utils.translation import ugettext as _
from django.db.models import Q


PRIVACY_PUBLIC = 1
PRIVACY_FRIENDS = 2
PRIVACY_PRIVATE = 3

PRIVACY_DEFAULT = PRIVACY_PUBLIC
PRIVACY_TYPES = {
    PRIVACY_PUBLIC: {
        'title': _('Publico'),
        'icon': 'icon-globe',
        'filter': lambda privacy, user: Q(privacy=privacy)
    },
    PRIVACY_FRIENDS: {
        'title': _('Amigos'),
        'icon': 'icon-user',
        'filter': lambda privacy, user: (
            Q(privacy=privacy) & (
                Q(owner__pk__in=user.friends_id) | Q(owner__pk=user.pk)
            )
        )
    },
    PRIVACY_PRIVATE: {
        'title': _('Privado'),
        'icon': 'icon-lock',
        'filter': lambda privacy, user: Q(privacy=privacy, owner=user)
    }
}

ANONYMOUS_PRIVACY = {
    PRIVACY_PUBLIC: PRIVACY_TYPES[PRIVACY_PUBLIC]
}


def choices():
    privacy = sorted(PRIVACY_TYPES.items(), key=lambda i: i[0])
    return [(pk, item['title']) for pk, item in privacy]


PRIVACY_CHOICES = choices()
