from django.contrib.auth import backends
from django.db.models import Q
from .models import User


class ModelBackend(backends.ModelBackend):
    def authenticate(self, request=None, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
