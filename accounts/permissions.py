from backend.fields import Error
from django.utils.translation import ugettext_lazy as _

PermissionRequired = Error(
    code='permission_required',
    message=_("You don't have permission to perform this action"),
)


def has_permission(cls, request, obj, perm):
    if perm not in obj.get_my_perms(request.user):
        return cls(errors=[PermissionRequired])
